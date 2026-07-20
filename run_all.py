#!/usr/bin/env python3
"""
run_all.py — CDQI batch driver. Walks the slate, runs every topic unattended, freezes + tags each.

Replaces hand-typing 15 extraction commands and 15 git-freeze blocks (the Methodology-C headache).
The slate CSV is the SINGLE SOURCE OF TRUTH — nothing is typed per topic, so the copy-paste drift
that mismatched a condition and its query in the C runbook cannot happen here.

Per topic: fetch-once -> reconcile -> checkpoint -> compute (2 tables + 2 supp + 4 figures) ->
git add/commit/tag <slug>-frozen. One API touch per topic; re-runs read the checkpoint.

    python3 run_all.py                          # run every topic in the slate, freeze + tag each
    python3 run_all.py --only "atrial fibrillation"   # (re)run one topic
    python3 run_all.py --no-git                 # compute only, skip freeze/tag (dev)
    python3 run_all.py --slate cdqi_slate.csv --outdir output

Slate columns required: condition, query, query_field, scope, terms
  (terms = space- or semicolon-separated positive terms for capture-recapture; may be blank)

PREREGISTER FIRST. Lock the prereg (all 15 topic specs, timestamped) BEFORE running this. A
registration that postdates the data is worth nothing (runbook Appendix B).
"""
import os, sys, argparse, subprocess, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # portable: find sibling modules
import pandas as pd
import cdqi_reference as C

# figure styling is optional; if the figure-style skill helper isn't present, plots still render.
try:
    from figure_style import apply_figure_style  # type: ignore
except Exception:
    apply_figure_style=None

def _sh(cmd, cwd=None):
    r=subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode!=0: print(f"  [git] WARN: {' '.join(cmd)} -> {r.stderr.strip()[:200]}")
    return r.returncode==0

def freeze(outdir, slug, condition, verified=False):
    """git add/commit/tag for one topic. Tags are slugified (git tags cannot contain spaces)."""
    stage="verified" if verified else "frozen"
    msg=f"{'Independent verification' if verified else 'Freeze'}: {condition} authoritative pull"
    _sh(["git","add","-A"], cwd=outdir)
    _sh(["git","commit","-m",msg], cwd=outdir)
    _sh(["git","tag","-f",f"{slug}-{stage}"], cwd=outdir)

def load_slate(path):
    df=pd.read_csv(path)
    # normalize the scope tokens the slate CSV uses (PROC_DEVICE / DRUG / DEVICE / BEHAVIORAL ...)
    need={"condition","query","query_field","scope"}
    missing=need-set(df.columns)
    assert not missing, f"slate missing columns: {missing}"
    if "terms" not in df.columns: df["terms"]=""
    return df

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--slate",default="cdqi_slate.csv")
    ap.add_argument("--outdir",default="output")
    ap.add_argument("--only",default=None,help="run a single condition by exact name")
    ap.add_argument("--no-git",action="store_true",help="skip freeze/tag (dev mode)")
    a=ap.parse_args()
    df=load_slate(a.slate)
    if a.only: df=df[df.condition==a.only]
    assert len(df)>0, "no topics selected"
    os.makedirs(a.outdir,exist_ok=True)
    # init the repo once (idempotent)
    if not a.no_git and not os.path.isdir(os.path.join(a.outdir,".git")):
        _sh(["git","init"], cwd=a.outdir)
    summary=[]
    for _,row in df.iterrows():
        cond=row["condition"]
        terms=[t for t in str(row.get("terms","")).replace(";"," ").split() if t and t!="nan"]
        print(f"\n=== {cond} (scope={row['scope']}, field={row['query_field']}) ===")
        try:
            r=C.run_topic(cond, query=str(row["query"]), query_field=str(row["query_field"]),
                          scope=str(row["scope"]), terms=terms, outdir=a.outdir,
                          apply_style=apply_figure_style)
            if not a.no_git: freeze(a.outdir, C.slug(cond), cond)
            summary.append(dict(condition=cond, n=r["n"], completeness=r["completeness"],
                                degenerate=r.get("degenerate"), stamp=r["stamp"], status="OK"))
            print(f"  OK  n={r['n']}  completeness={r['completeness']}  degenerate={r.get('degenerate')}  stamp={r['stamp']}")
        except Exception as e:
            summary.append(dict(condition=cond, n=None, completeness=None, degenerate=None, stamp=None, status=f"FAIL: {e}"))
            print(f"  FAIL: {e}")
    sdf=pd.DataFrame(summary)
    sdf.to_csv(os.path.join(a.outdir,"run_all_summary.csv"), index=False)
    print("\n===== BATCH SUMMARY =====")
    print(sdf.to_string(index=False))
    n_ok=(sdf.status=="OK").sum()
    print(f"\n{n_ok}/{len(sdf)} topics OK. Summary -> {a.outdir}/run_all_summary.csv")
    if not a.no_git:
        print("Push all frozen tags with:  cd %s && git push -u origin main --tags" % a.outdir)

if __name__=="__main__": main()
