#!/usr/bin/env python3
"""
review_all.py — CDQI independent reviewer, ALL topics in one pass.

Run by a leader who did NOT extract. It independently re-pulls every topic from the live registry,
recomputes the CDQI components, and diffs them against the frozen dataset the analyst committed.
Writes ONE consolidated review_report_ALL.md with a PASS/FLAG row per topic.

Why one pass is legitimate here (and was NOT for Methodology B/E): CDQI is DETERMINISTIC — it reads
only structured registration fields, with no LLM step and no human free-text coding. There is no
subjective extraction to dual-code, so independence is satisfied by an independent RE-PULL +
recompute, which can be batched. (B/E still need per-topic dual-coding + Cohen's kappa.)

    python3 review_all.py --frozen output --slate cdqi_slate.csv

A topic PASSES when the independently re-pulled component prevalences match the frozen ones within
tolerance. Small drift is expected (the registry moves between the freeze and the review); a FLAG
means drift beyond tolerance OR a reconciliation failure OR a missing frozen package — investigate.
"""
import os, sys, argparse, json, datetime, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # portable: find sibling modules
import numpy as np, pandas as pd
import cdqi_reference as C

TOL_PREV=0.03      # allowed absolute drift in a component prevalence
TOL_N=0.05         # allowed relative drift in scored-N (registry grows over time)

def review_topic(cond, row, frozen_dir):
    slug=C.slug(cond); d=os.path.join(frozen_dir,f"CDQI_{slug}")
    frozen_t2=os.path.join(d,f"CDQI_{slug}_table2_components.csv")
    if not os.path.exists(frozen_t2):
        return dict(condition=cond, verdict="FLAG", reason="no frozen package found", max_drift=None)
    old=pd.read_csv(frozen_t2).set_index("component")
    terms=[t for t in str(row.get("terms","")).replace(";"," ").split() if t and t!="nan"]
    # independent re-pull into a scratch dir (does NOT touch the frozen package)
    scratch=os.path.join(frozen_dir,"_review_scratch")
    try:
        r=C.run_topic(cond, query=str(row["query"]), query_field=str(row["query_field"]),
                      scope=str(row["scope"]), terms=terms, outdir=scratch)
    except Exception as e:
        return dict(condition=cond, verdict="FLAG", reason=f"re-pull failed: {e}", max_drift=None)
    new=pd.read_csv(os.path.join(scratch,f"CDQI_{slug}",f"CDQI_{slug}_table2_components.csv")).set_index("component")
    drift=(new["prevalence"]-old["prevalence"]).abs()
    max_drift=float(drift.max())
    n_old=int(old["n"].max()); n_new=int(new["n"].max())
    n_rel=abs(n_new-n_old)/max(n_old,1)
    ok = (max_drift<=TOL_PREV) and (n_rel<=TOL_N)
    return dict(condition=cond, verdict="PASS" if ok else "FLAG",
                reason=("within tolerance" if ok else f"drift={max_drift:.3f} (tol {TOL_PREV}), n {n_old}->{n_new}"),
                max_drift=round(max_drift,4), n_frozen=n_old, n_repull=n_new)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--frozen",default="output",help="dir holding the frozen CDQI_<slug>/ packages")
    ap.add_argument("--slate",default="cdqi_slate.csv")
    ap.add_argument("--only",default=None)
    a=ap.parse_args()
    df=pd.read_csv(a.slate)
    if "terms" not in df.columns: df["terms"]=""
    if a.only: df=df[df.condition==a.only]
    rows=[]
    for _,row in df.iterrows():
        print(f"reviewing {row['condition']} ...")
        rows.append(review_topic(row["condition"], row, a.frozen))
    rep=pd.DataFrame(rows)
    ts=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    npass=(rep.verdict=="PASS").sum()
    def md_table(d):
        cols=list(d.columns); out=["| "+" | ".join(cols)+" |","|"+"|".join(["---"]*len(cols))+"|"]
        for _,r in d.iterrows(): out.append("| "+" | ".join("" if pd.isna(r[c]) else str(r[c]) for c in cols)+" |")
        return "\n".join(out)
    lines=[f"# CDQI independent review — all topics",
           f"", f"Reviewer re-pull vs frozen analyst package. Generated {ts}.",
           f"Tolerance: component-prevalence drift <= {TOL_PREV}, scored-N relative drift <= {TOL_N}.",
           f"", f"**{npass}/{len(rep)} topics PASS.**", f"",
           md_table(rep)]
    out=os.path.join(a.frozen,"review_report_ALL.md")
    open(out,"w").write("\n".join(lines))
    rep.to_csv(os.path.join(a.frozen,"review_report_ALL.csv"), index=False)
    print("\n"+rep.to_string(index=False))
    print(f"\n{npass}/{len(rep)} PASS. Report -> {out}")
    print("This file is the independence record; commit it and tag <slug>-verified.")

if __name__=="__main__": main()
