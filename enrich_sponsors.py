#!/usr/bin/env python3
"""
enrich_sponsors.py — CDQI sponsor-type stratification from FROZEN checkpoints.

WHY THIS EXISTS
    ClinicalTrials.gov's LeadSponsorClass is coarse: universities, hospitals, and academic
    medical centers all collapse into "OTHER", so the raw sponsor_class field is ~uninterpretable
    for an industry-vs-academic contrast. This script promotes the lead-sponsor NAME — which is
    ALREADY present in each topic's frozen raw pull (FIELDS includes SponsorCollaboratorsModule) —
    and applies the shared deterministic sponsor_classifier to split OTHER into
    industry / academic / hospital / government / research_nonprofit / network / individual.

NO API CALLS. This is an OFFLINE recompute from the frozen checkpoints. It does not touch the
verified extraction, the dataset CSVs, or the run-stamps. Provenance of the core index is untouched.

SCOPE NOTE (state in methods): sponsor type is classified by a deterministic, pre-specified keyword
instrument applied to the free-text sponsor-NAME field (lead sponsor only, matching the DeVito 2020
industry/non-industry split). This is the one text-derived variable in the study; the residual
(unresolved "other") is reported per topic so completeness of the classification is auditable.

OUTPUTS (per topic, written into the same output/CDQI_<slug>/ folder):
    CDQI_<slug>_sponsors.csv        per-trial: nct, lead_sponsor_name, ctgov_class, industry, category
    CDQI_<slug>_sponsor_table.csv   industry vs non-industry + per-category prevalence + Wilson 95% CI
CONSOLIDATED (into output/):
    sponsor_summary_ALL.csv         one row per topic: n, % industry [Wilson CI], residual %

USAGE
    python3 enrich_sponsors.py --frozen output
    python3 enrich_sponsors.py --frozen output --only total_knee_arthroplasty
"""
import os, sys, gzip, json, glob, argparse, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find sibling modules
import pandas as pd
from sponsor_classifier import classify_frame

# Wilson score 95% CI — identical formula to cdqi_reference.wilson, inlined so this script is
# standalone (no matplotlib/harness import chain required just to stratify sponsors).
_Z = 1.959963984540054
def wilson(k, n):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    d = 1 + _Z**2 / n
    c = (p + _Z**2 / (2*n)) / d
    h = (_Z / d) * math.sqrt(p*(1-p)/n + _Z**2/(4*n**2))
    return (p, c - h, c + h)


def _dig(d, *path):
    cur = d
    for k in path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return None
    return cur


def load_checkpoint(raw_path):
    """Read a frozen CDQI_<slug>_raw.json.gz -> DataFrame[nct, lead_sponsor_name, sponsor_class].
    Column names match sponsor_classifier.classify_frame() defaults exactly."""
    with gzip.open(raw_path, "rt") as f:
        raw = json.load(f)
    rows = []
    for s in raw:
        ps = s.get("protocolSection", {}) or {}
        rows.append({
            "nct": _dig(ps, "identificationModule", "nctId"),
            "lead_sponsor_name": _dig(ps, "sponsorCollaboratorsModule", "leadSponsor", "name"),
            "sponsor_class": _dig(ps, "sponsorCollaboratorsModule", "leadSponsor", "class"),
        })
    return pd.DataFrame(rows)


def sponsor_table(df):
    """industry vs non-industry (the primary split) + each category's prevalence, Wilson 95% CI."""
    n = len(df)
    rows = []
    k_ind = int(df["sponsor_industry"].sum())
    for label, k in [("industry (lead)", k_ind), ("non-industry (lead)", n - k_ind)]:
        p, lo, hi = wilson(k, n)
        rows.append(dict(group=label, k=k, n=n, prevalence=round(p, 4),
                         ci_low=round(lo, 4), ci_high=round(hi, 4)))
    for cat, k in df["sponsor_category"].value_counts().items():
        p, lo, hi = wilson(int(k), n)
        rows.append(dict(group=f"category: {cat}", k=int(k), n=n, prevalence=round(p, 4),
                         ci_low=round(lo, 4), ci_high=round(hi, 4)))
    return pd.DataFrame(rows)


def process_topic(topic_dir):
    slug = os.path.basename(topic_dir).replace("CDQI_", "", 1)
    raws = glob.glob(os.path.join(topic_dir, "*_raw.json.gz"))
    if not raws:
        return None
    df = load_checkpoint(raws[0])
    if len(df) == 0:
        return None
    df, rep = classify_frame(df)   # adds sponsor_industry (bool), sponsor_category (str)
    df.to_csv(os.path.join(topic_dir, f"CDQI_{slug}_sponsors.csv"), index=False)
    tab = sponsor_table(df)
    tab.to_csv(os.path.join(topic_dir, f"CDQI_{slug}_sponsor_table.csv"), index=False)
    ind = tab[tab.group == "industry (lead)"].iloc[0]
    return dict(topic=slug, n=rep["n"], industry_k=int(ind.k),
                industry_prev=ind.prevalence, industry_ci_low=ind.ci_low, industry_ci_high=ind.ci_high,
                residual_other=rep["residual_other"], residual_pct=rep["residual_pct"])


def main():
    ap = argparse.ArgumentParser(description="CDQI offline sponsor stratification from frozen checkpoints")
    ap.add_argument("--frozen", default="output", help="dir holding the CDQI_<slug>/ packages")
    ap.add_argument("--only", default=None, help="single topic slug (folder minus CDQI_ prefix)")
    a = ap.parse_args()
    dirs = sorted(d for d in glob.glob(os.path.join(a.frozen, "CDQI_*")) if os.path.isdir(d))
    if a.only:
        dirs = [d for d in dirs if os.path.basename(d) == f"CDQI_{a.only}"]
    if not dirs:
        print(f"No CDQI_<slug>/ folders found under {a.frozen}"); sys.exit(1)
    summary = []
    for d in dirs:
        r = process_topic(d)
        if r is None:
            print(f"  SKIP {os.path.basename(d)} (no checkpoint / empty)"); continue
        summary.append(r)
        flag = "" if r["residual_pct"] < 5 else "  <-- REVIEW: >5% unresolved"
        print(f"  {r['topic']:34} n={r['n']:5}  industry={r['industry_prev']:.1%} "
              f"[{r['industry_ci_low']:.1%}, {r['industry_ci_high']:.1%}]  residual={r['residual_pct']}%{flag}")
    sdf = pd.DataFrame(summary)
    out = os.path.join(a.frozen, "sponsor_summary_ALL.csv")
    sdf.to_csv(out, index=False)
    print(f"\nWrote {len(sdf)} topics -> {out}")
    if len(sdf):
        worst = sdf.sort_values("residual_pct", ascending=False).iloc[0]
        verdict = "all topics <5% unresolved (classification effectively complete)" \
            if worst["residual_pct"] < 5 else \
            f"{worst['topic']} has {worst['residual_pct']}% unresolved — inspect its names before reporting"
        print("Residual check:", verdict)


if __name__ == "__main__":
    main()
