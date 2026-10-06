#!/usr/bin/env python3
"""
cdqi_reference.py — Computable Design-Quality Index (CDQI): per-topic extraction engine.

ONE topic per invocation. Condition-agnostic — every per-topic difference is a command-line
argument or a row in cdqi_slate.csv. NEVER edit this file to change a topic (see runbook Appendix B).

Pipeline (efficiency = rigor):
    fetch ONCE  ->  reconcile totalCount  ->  checkpoint raw JSON  ->  compute offline  ->  freeze
The registry is touched exactly once per topic. Every re-run reads the checkpoint, so results are
bit-for-bit reproducible and the API is never re-hammered.

CDQI is DETERMINISTIC: it reads only structured registration fields. There is NO LLM step and NO
human-coding step in the index, which is why one reviewer pass can validate all topics at once
(unlike Methodologies B/E, whose free-text classification needs per-topic dual-coding).

Outputs written to <outdir>/CDQI_<slug>/ :
    CDQI_<slug>_dataset.csv              per-trial component matrix
    CDQI_<slug>_raw.json.gz              reconciled raw pull (the CHECKPOINT — never re-fetched)
    CDQI_<slug>_table1_cohort.csv        Table 1 — cohort descriptor
    CDQI_<slug>_table2_components.csv    Table 2 — 9 components x prevalence + Wilson 95% CI
    CDQI_<slug>_supp1_by_intervention.csv   S1 — components x intervention type (numeric)
    CDQI_<slug>_supp2_by_epoch.csv          S2 — components x epoch (numeric)
    figures/  fig1_prisma.png fig2_by_intervention.png fig3_epoch_trend.png fig4_quality_contribution.png
    CDQI_<slug>_qc_checkpoints.csv       QC log (reconciliation gate)
    CDQI_<slug>_decision_log.md          audit trail (anchor string, term list, analytic choices)
    CDQI_<slug>_run_stamp.json           provenance hash (cited in the manuscript)
    CDQI_<slug>_data_memo.md             headline numbers in manuscript wording

Usage:
    python3 cdqi_reference.py --condition "total knee arthroplasty" --query "total knee arthroplasty" \\
        --query-field query.term --scope PROC_DEVICE --terms reverse,rtsa --outdir output
"""
import os, sys, json, gzip, argparse, re, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # portable: find ctgov_harness beside this file
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib as mpl, matplotlib.pyplot as plt
import ctgov_harness as H

Z = 1.959963984540054
MASK_ORD = {"NONE":0,"SINGLE":1,"DOUBLE":2,"TRIPLE":3,"QUADRUPLE":4}
# scope -> the intervention TYPE(s) that count as "the intervention being studied" (protocol §3)
SCOPE_TYPES = {"DRUG":{"DRUG"},"BIOLOGICAL":{"BIOLOGICAL"},"DRUG_BIOLOGICAL":{"DRUG","BIOLOGICAL"},
               "DEVICE":{"DEVICE"},"PROC_DEVICE":{"PROCEDURE","DEVICE"},
               "PROCEDURE":{"PROCEDURE"},"BEHAVIORAL":{"BEHAVIORAL"},"ALL":None}
# palette (CVD-safe; matches the RTSA proof-of-concept figures)
DEVICE_C="#B2182B"; DRUG_C="#2166AC"; OTHER_C="#999999"; Q_C="#762A83"
FIELDS=["NCTId","StatusModule","DesignModule","ArmsInterventionsModule",
        "SponsorCollaboratorsModule","ReferencesModule","OversightModule","HasResults",
        "IPDSharingStatementModule",      # Axis-2: ipdSharing pledge (protocol §5)
        "ParticipantFlowModule"]          # A3 attrition: STARTED vs COMPLETED (results-posted only)

# A3 attrition: RoB2-conventional threshold for the binary "acceptable attrition" prevalence row.
# The CONTINUOUS attrition rate is always reported (Table 1); this threshold only governs the
# binary Table-2 row. Named here so it is explicit and easy to change. NOTE: confirm/declare this
# 0.20 cutoff in the OSF amendment before the confirmatory run.
ATTRITION_THRESHOLD=0.20
# Arm-group types that count as a genuine comparator (A6 comparator adequacy, protocol §5).
COMPARATOR_TYPES={"PLACEBO_COMPARATOR","SHAM_COMPARATOR","ACTIVE_COMPARATOR","NO_INTERVENTION"}

def slug(s): return re.sub(r"[^a-z0-9]+","_",s.lower()).strip("_")

def wilson(k,n):
    if n==0: return (np.nan,np.nan,np.nan)
    p=k/n; d=1+Z**2/n; c=(p+Z**2/(2*n))/d; h=(Z/d)*np.sqrt(p*(1-p)/n+Z**2/(4*n**2))
    return (p,c-h,c+h)

def _blob(s):
    ps=s["protocolSection"]; idm=ps.get("identificationModule",{})
    parts=[idm.get("briefTitle","") or "", idm.get("officialTitle","") or ""]
    parts+=ps.get("conditionsModule",{}).get("conditions",[]) or []
    ai=ps.get("armsInterventionsModule",{})
    for a in ai.get("armGroups",[]) or []: parts+=[a.get("label","") or "", a.get("description","") or ""]
    for i in ai.get("interventions",[]) or []: parts+=[i.get("name","") or "", i.get("description","") or ""]
    return " ".join(parts).lower()

def _int_class(itypes):
    has_pd=any(t in("PROCEDURE","DEVICE") for t in itypes); has_dr=any(t=="DRUG" for t in itypes)
    return ("proc_device" if(has_pd and not has_dr) else "drug" if(has_dr and not has_pd)
            else "both" if(has_pd and has_dr) else "other")

def _power_ok(phase,n):
    if n is None: return None
    if any(p in phase for p in ("PHASE3","PHASE4")): return n>=100
    if "PHASE2" in phase: return n>=50
    return n>=30

def _epoch(y):
    if y is None: return None
    if y<=2015: return "<=2015"
    if y<=2020: return "2016-2020"
    return "2021-2026"

def _attrition(s):
    """A3 attrition from the results-section participant flow. Sums STARTED and COMPLETED across
    arm groups in the FIRST period (the overall-study period). Returns (started, completed, frac)
    or (None, None, None) when no results/flow exist. frac = 1 - completed/started."""
    rs=s.get("resultsSection") or {}
    periods=(rs.get("participantFlowModule") or {}).get("periods") or []
    if not periods: return (None,None,None)
    def _sum(mtype):
        tot=0; found=False
        for m in (periods[0].get("milestones") or []):
            if m.get("type")==mtype:
                for a in (m.get("achievements") or []):
                    try: tot+=int(a.get("numSubjects")); found=True
                    except (TypeError,ValueError): pass
        return tot if found else None
    started=_sum("STARTED"); completed=_sum("COMPLETED")
    if not started or completed is None: return (started,completed,None)
    return (started, completed, 1.0-completed/started)

def _comparator(arm_types):
    """A6 comparator adequacy. Returns (has_comparator: bool, comparator_kind: str) from arm-group
    types. Absent/unknown types are treated as no comparator (consistent with single-group == no
    comparator); this missingness rule is stated in the methods."""
    has_placebo=any(t in ("PLACEBO_COMPARATOR","SHAM_COMPARATOR") for t in arm_types)
    has_active=any(t=="ACTIVE_COMPARATOR" for t in arm_types)
    has_comp=any(t in COMPARATOR_TYPES for t in arm_types)
    kind=("placebo/sham" if has_placebo else "active" if has_active
          else "no-intervention" if any(t=="NO_INTERVENTION" for t in arm_types)
          else "none/single-group")
    return has_comp, kind

# ----- COMPONENT LABELS (protocol §5) -----
# A_COMPS now includes A6 comparator adequacy and A3 attrition (results-posted only).
# A5 intervention model is a 5-level categorical -> reported as a DISTRIBUTION in Table 1, not a binary row.
A_COMPS=["randomized","blinded_any","blinded_double_plus","power_ok","has_comparator","low_attrition"]  # A1,A2,A2+,A4,A6,A3
B_COMPS=["pivotal","treatment","multiarm"]                              # B1,B2,B3
# AXIS2 is the ordered evidentiary-contribution LADDER (protocol §5.1 / amendment §3):
#   results posted -> own publication linked -> independent (DERIVED) citation -> IPD-sharing pledge
AXIS2=["has_results","has_result_ref","has_derived","ipd_yes"]
OVERSIGHT=["dmc"]                                                       # Axis-2 oversight (not a ladder rung)
CORE_COMPS=A_COMPS+B_COMPS+AXIS2+OVERSIGHT
COMP_LABEL={"randomized":"Randomized (A1)","blinded_any":"Any blinding (A2)",
    "blinded_double_plus":"Double-blind+ (A2)","power_ok":"Meets power floor (A4)",
    "has_comparator":"Has comparator arm (A6)","low_attrition":f"Attrition <{int(ATTRITION_THRESHOLD*100)}% (A3, results-posted)",
    "pivotal":"Pivotal phase 3/4 (B1)","treatment":"Treatment purpose (B2)","multiarm":"Multi-arm >=3 (B3)",
    "has_results":"Results posted","has_result_ref":"Own publication linked",
    "has_derived":"Independent citation (DERIVED)","ipd_yes":"IPD-sharing pledged","dmc":"DMC oversight"}


def search_and_scope(condition, query, query_field, scope, terms, qc, dl):
    """Three-step search (protocol §4): broad retrieve -> classify -> capture-recapture completeness.
    Returns (scoped_studies, search_meta). Uses ONE broad pull; classification is offline."""
    keep_types=SCOPE_TYPES.get(scope)
    # Strategy A: the concept/phrase search on the declared field
    A=H.fetch_studies(query, qc=qc, query_field=query_field, fields=FIELDS)
    A_ncts={s["protocolSection"]["identificationModule"]["nctId"] for s in A}
    by_nct={s["protocolSection"]["identificationModule"]["nctId"]:s for s in A}
    # Strategy B: broad-net + deterministic keyword classify (only if a term list is given)
    termlist=[t.strip().lower() for t in terms if t.strip()] if terms else []
    if termlist:
        B_raw=H.fetch_studies(query, qc=qc, query_field="query.term", fields=FIELDS)
        for s in B_raw: by_nct.setdefault(s["protocolSection"]["identificationModule"]["nctId"],s)
        B_ncts=set()
        for s in B_raw:
            t=_blob(s)
            if any(term in t for term in termlist):
                B_ncts.add(s["protocolSection"]["identificationModule"]["nctId"])
        cr=H.capture_recapture(A_ncts, B_ncts)
        # A degenerate estimate is one where the two strategies are subset-related (overlap==n1 or
        # overlap==n2): the estimator trivially returns the union and completeness collapses to ~100%.
        # Per protocol §4.3 that is NOT a strong statistical estimate; flag it so it is never confused
        # with a real two-strategy number (e.g. atrial fibrillation 0.95).
        cr["degenerate"]=(cr["overlap"]==cr["n1"] or cr["overlap"]==cr["n2"])
        universe=A_ncts | B_ncts
    else:
        # No positive-term list -> no independent second strategy. This is the clean-terminology /
        # unsplittable case (protocol §4.3). Report the DEGENERATE completeness (union == the single
        # capture -> 100%) rather than leaving it blank, and FLAG it as degenerate.
        cr={"n1":len(A_ncts),"n2":None,"overlap":None,"union":len(A_ncts),
            "N_hat":len(A_ncts),"completeness":1.0,"n_missed_est":0.0,"degenerate":True}
        universe=A_ncts
    # apply interventionType scope filter
    scoped=[]
    for nct in universe:
        s=by_nct[nct]
        itypes=[i.get("type") for i in s["protocolSection"].get("armsInterventionsModule",{}).get("interventions",[]) or []]
        if keep_types is None or any(t in keep_types for t in itypes):
            scoped.append(s)
    dl.record("search_strategy_A", f"{query_field}='{query}' -> {len(A_ncts)} trials")
    if termlist:
        dl.record("search_strategy_B", f"broad query.term + classify terms={termlist} -> {cr['n2']} trials")
        dl.record("capture_recapture", f"union={cr['union']} N_hat={cr['N_hat']} completeness={cr['completeness']} degenerate={cr.get('degenerate')}")
    else:
        dl.record("capture_recapture", "single-strategy (no positive-term list) -> degenerate completeness=1.0; "
                  "reflects unambiguous terminology, not a strong statistical estimate (protocol §4.3)")
    dl.record("intervention_scope", f"scope={scope} types={sorted(keep_types) if keep_types else 'ALL'} -> {len(scoped)} scoped trials")
    qc.checkpoint("scoped_trials", len(scoped), f"scope={scope}")
    universe_studies=[by_nct[n] for n in universe]
    return scoped, universe_studies, cr


def compute_matrix(studies):
    """Per-trial component matrix (protocol §5). Deterministic — structured fields only."""
    rows=[]
    for s in studies:
        ps=s["protocolSection"]; di=ps.get("designModule",{}).get("designInfo",{}) or {}
        nct=ps.get("identificationModule",{}).get("nctId")
        phase=";".join(ps.get("designModule",{}).get("phases",[]) or [])
        n_enr=H.dig(ps,"designModule","enrollmentInfo","count")
        arms=ps.get("armsInterventionsModule",{}).get("armGroups",[]) or []
        ints=ps.get("armsInterventionsModule",{}).get("interventions",[]) or []
        itypes=[i.get("type") for i in ints]
        arm_types=[a.get("type") for a in arms]
        refs=ps.get("referencesModule",{}).get("references",[]) or []
        start=H.dig(ps,"statusModule","startDateStruct","date")
        yr=int(start[:4]) if start else None
        mask=di.get("maskingInfo",{}).get("masking")
        n_derived=sum(1 for r in refs if r.get("type")=="DERIVED")
        has_comp,comp_kind=_comparator(arm_types)
        started,completed,attrition=_attrition(s)
        ipd=H.dig(ps,"ipdSharingStatementModule","ipdSharing")   # YES / NO / UNDECIDED / None
        rows.append(dict(
            nct=nct, year=yr, epoch=_epoch(yr), phase=phase, int_class=_int_class(itypes),
            n_arms=len(arms), n_enroll=n_enr,
            sponsor_class=H.dig(ps,"sponsorCollaboratorsModule","leadSponsor","class"),
            overall_status=H.dig(ps,"statusModule","overallStatus"),
            allocation=di.get("allocation"), randomized=(di.get("allocation")=="RANDOMIZED"),
            masking=mask, masking_ord=MASK_ORD.get(mask),
            blinded_any=(MASK_ORD.get(mask,0)>=1), blinded_double_plus=(MASK_ORD.get(mask,0)>=2),
            model=di.get("interventionModel"), power_ok=_power_ok(phase,n_enr),
            # A6 comparator adequacy
            comparator_kind=comp_kind, has_comparator=has_comp,
            # A3 attrition (results-posted only -> None elsewhere, so it drops out of its denominator)
            n_started=started, n_completed=completed, attrition=attrition,
            low_attrition=(None if attrition is None else attrition<ATTRITION_THRESHOLD),
            pivotal=any(p in phase for p in("PHASE3","PHASE4")),
            treatment=(di.get("primaryPurpose")=="TREATMENT"), multiarm=(len(arms)>=3),
            # Axis-2 contribution ladder
            has_results=bool(s.get("hasResults")),
            has_result_ref=any(r.get("type")=="RESULT" for r in refs),
            n_derived=n_derived, has_derived=(n_derived>0),
            ipd=ipd, ipd_yes=(ipd=="YES"),
            dmc=H.dig(ps,"oversightModule","oversightHasDmc"),
        ))
    return pd.DataFrame(rows)


def table1_cohort(df, condition):
    """Table 1 — cohort descriptor (who is in the denominator)."""
    def enr_iqr():
        e=df["n_enroll"].dropna()
        return (int(e.median()), int(e.quantile(.25)), int(e.quantile(.75))) if len(e) else (np.nan,)*3
    med,q1,q3=enr_iqr()
    yrs=df["year"].dropna()
    rows=[("N trials", len(df)),
          ("Date range (start year)", f"{int(yrs.min())}-{int(yrs.max())}" if len(yrs) else "NA"),
          ("Enrollment median [IQR]", f"{med} [{q1}-{q3}]"),
          ("Pivotal (phase 3/4), n (%)", f"{df.pivotal.sum()} ({df.pivotal.mean():.0%})"),
          ("Treatment purpose, n (%)", f"{df.treatment.sum()} ({df.treatment.mean():.0%})"),
          ("Results posted, n (%)", f"{df.has_results.sum()} ({df.has_results.mean():.0%})")]
    # A3 attrition (continuous) among results-posted trials — the threshold-free report of A3
    att=df["attrition"].dropna()
    if len(att):
        rows.append(("Attrition median [IQR], results-posted",
                     f"{att.median():.1%} [{att.quantile(.25):.1%}-{att.quantile(.75):.1%}] (n={len(att)})"))
    for lbl,col in [("Intervention type","int_class"),("Sponsor class","sponsor_class"),
                    ("Intervention model (A5)","model"),("Comparator (A6)","comparator_kind"),
                    ("IPD-sharing statement","ipd")]:
        vc=df[col].fillna("(not stated)").value_counts()
        for k,v in vc.items():
            rows.append((f"{lbl}: {k}", f"{v} ({v/len(df):.0%})"))
    return pd.DataFrame(rows, columns=["characteristic","value"])


def table2_components(df):
    """Table 2 — design + contribution components x prevalence + Wilson 95% CI.
    Each component's denominator is its own non-missing n (attrition and low_attrition are
    results-posted-only, so their n is the results-posted subset; DMC is reported among trials
    that state DMC status). Missingness is asymmetric by design and stated in the methods:
    randomization/blinding code absence as negative and keep it in the denominator; power,
    attrition, and DMC report over the subset for which the datum exists."""
    rows=[]
    for c in CORE_COMPS:
        v=df[c].dropna(); k=int(v.sum()); n=int(len(v)); p,lo,hi=wilson(k,n)
        rows.append(dict(component=COMP_LABEL[c], k=k, n=n, prevalence=round(p,4),
                         ci_low=round(lo,4), ci_high=round(hi,4)))
    return pd.DataFrame(rows)


def supp_by_group(df, groupcol, order=None):
    """Supplementary numeric table: each core component's prevalence within each group level."""
    groups=order or sorted(x for x in df[groupcol].dropna().unique())
    out=[]
    for g in groups:
        sub=df[df[groupcol]==g]; row={groupcol:g,"n":len(sub)}
        for c in CORE_COMPS:
            v=sub[c].dropna(); row[c]=round(v.mean(),4) if len(v) else np.nan
        out.append(row)
    return pd.DataFrame(out)


def _style(ax):
    for s in ("top","right"): ax.spines[s].set_visible(False)

def fig1_prisma(df, cr, condition, scope, outpath):
    fig,ax=plt.subplots(figsize=(7.2,6.0)); ax.axis("off")
    comp = ("n/a" if cr.get("completeness") is None
            else f"{cr['completeness']:.0%} (degenerate)" if cr.get("degenerate")
            else f"{cr['completeness']:.0%}")
    n_res=int(df.has_results.sum())
    boxes=[(f"Retrieved (search union)\nn = {cr['union']}", 0.90, DRUG_C),
           (f"After interventionType scope = {scope}\nn = {len(df)}", 0.62, DEVICE_C),
           (f"CDQI-scored population\ncompleteness est. = {comp}\nn = {len(df)}", 0.34, DEVICE_C),
           (f"Results-posted subset\n(attrition + contribution)\nn = {n_res}", 0.07, Q_C)]
    for txt,y,col in boxes:
        ax.add_patch(mpl.patches.FancyBboxPatch((0.26,y-0.07),0.48,0.12,boxstyle="round,pad=0.01",
            linewidth=1.6,edgecolor=col,facecolor=col+"18",transform=ax.transAxes))
        ax.text(0.5,y,txt,ha="center",va="center",fontsize=8,transform=ax.transAxes)
    for i in range(len(boxes)-1):
        ax.annotate("",xy=(0.5,boxes[i+1][1]+0.065),xytext=(0.5,boxes[i][1]-0.07),
            xycoords=ax.transAxes,arrowprops=dict(arrowstyle="-|>",color="#444",lw=1.5))
    ax.set_title(f"Population flow — {condition}",fontsize=9)
    fig.savefig(outpath,dpi=200,bbox_inches="tight"); plt.close(fig)

def fig2_by_intervention(df, condition, outpath):
    comps=["randomized","blinded_any","blinded_double_plus","power_ok","has_results"]
    classes=[("drug","Drug",DRUG_C),("proc_device","Procedure/Device",DEVICE_C),("other","Behavioral/Other",OTHER_C)]
    present=[(c,l,col) for c,l,col in classes if (df.int_class==c).sum()>=5]
    fig,ax=plt.subplots(figsize=(7.6,4.4)); y=np.arange(len(comps)); h=0.8/max(len(present),1)
    for j,(cls,lab,col) in enumerate(present):
        sub=df[df.int_class==cls]; vals=[sub[c].dropna().mean() for c in comps]
        ax.barh(y+(len(present)/2-0.5-j)*h, vals, height=h, color=col,
                label=f"{lab} (n={len(sub)})", edgecolor="white")
    ax.set_yticks(y); ax.set_yticklabels([COMP_LABEL[c] for c in comps]); ax.invert_yaxis()
    ax.set_xlim(0,1); ax.set_xlabel("Proportion of trials")
    ax.set_title(f"CDQI components by intervention type — {condition}\n(read blinding WITHIN type: surgery cannot blind the operator)",fontsize=8,loc="left")
    ax.legend(frameon=False,fontsize=7,loc="lower right"); _style(ax)
    fig.savefig(outpath,dpi=200,bbox_inches="tight"); plt.close(fig)

def fig3_epoch(df, condition, outpath):
    eps=["<=2015","2016-2020","2021-2026"]
    series={"randomized":("Randomized",DRUG_C),"blinded_double_plus":("Double-blind+",DEVICE_C),
            "has_results":("Results posted",Q_C)}
    fig,ax=plt.subplots(figsize=(7.0,4.2)); x=np.arange(len(eps))
    ns=[(df.epoch==ep).sum() for ep in eps]
    for c,(lab,col) in series.items():
        yv=[df[df.epoch==ep][c].dropna().mean() for ep in eps]
        ax.plot(x,yv,"-o",color=col,label=lab,lw=2,ms=7)
    ax.set_xticks(x); ax.set_xticklabels([f"{ep}\n(n={n})" for ep,n in zip(eps,ns)])
    ax.set_ylim(0,1); ax.set_ylabel("Proportion of trials")
    ax.set_title(f"Design quality over time — {condition}\n(results-posting decline in recent epoch = follow-up-time artifact)",fontsize=8,loc="left")
    ax.legend(frameon=False,fontsize=7); _style(ax)
    fig.savefig(outpath,dpi=200,bbox_inches="tight"); plt.close(fig)

def waste_bracket(df):
    """RQ3 waste under the two pre-specified 'delivered' definitions (amendment §3).
    well-designed = randomized AND meets power floor.
      primary   delivered = results posted OR own publication linked
      sensitivity delivered = primary OR >=1 independent (DERIVED) citation
    Returns dict with the well-designed n and the undelivered count/fraction under each definition."""
    wd=df["randomized"].astype("boolean").fillna(False)&df["power_ok"].astype("boolean").fillna(False)
    prim=df["has_results"].astype("boolean").fillna(False)|df["has_result_ref"].astype("boolean").fillna(False)
    sens=prim|df["has_derived"].astype("boolean").fillna(False)
    nwd=int(wd.sum())
    waste_p=int((wd&~prim).sum()); waste_s=int((wd&~sens).sum())
    return {"n_well_designed":nwd,
            "waste_primary_n":waste_p, "waste_primary_frac_wd":(waste_p/nwd if nwd else np.nan),
            "waste_sens_n":waste_s,    "waste_sens_frac_wd":(waste_s/nwd if nwd else np.nan),
            "waste_primary_frac_cohort":waste_p/len(df) if len(df) else np.nan,
            "waste_sens_frac_cohort":waste_s/len(df) if len(df) else np.nan}

def fig4_quality_contribution(df, condition, outpath):
    # Quadrant uses the PRIMARY definition (results posted OR pub linked); the waste cell is
    # annotated with the pre-specified BRACKET down to the DERIVED-inclusive (sensitivity) value.
    wb=waste_bracket(df)
    dfq=df.copy()
    dfq["well_designed"]=dfq["randomized"].astype("boolean").fillna(False)&dfq["power_ok"].astype("boolean").fillna(False)
    dfq["delivered"]=dfq["has_results"].astype("boolean").fillna(False)|dfq["has_result_ref"].astype("boolean").fillna(False)
    ct=pd.crosstab(dfq["well_designed"],dfq["delivered"])
    for a in [True,False]:
        for b in [True,False]:
            if a not in ct.index or b not in ct.columns: ct.loc[a,b]=0
    ct=ct.reindex(index=[True,False],columns=[True,False]).fillna(0).astype(int)
    fig,ax=plt.subplots(figsize=(5.6,5.2))
    ax.imshow([[1,0],[0,0]],cmap=mpl.colors.ListedColormap(["#f2f2f2","#f7e9ec"]),alpha=0.0)
    labels=[["delivered\n& well-designed","NOT delivered\nbut well-designed  <- WASTE"],
            ["delivered,\nweak design","neither"]]
    for i,a in enumerate([True,False]):
        for j,b in enumerate([True,False]):
            n=ct.loc[a,b]; pct=n/len(dfq)
            hot = (a and not b)
            ax.add_patch(mpl.patches.Rectangle((j-0.5,i-0.5),1,1,
                facecolor=(DEVICE_C+"33" if hot else "#f2f2f2"),edgecolor="#888"))
            ax.text(j,i-0.12,f"{n}",ha="center",fontsize=15,fontweight="bold")
            ax.text(j,i+0.18,f"{pct:.0%}\n{labels[i][j]}",ha="center",fontsize=6.5,color="#333")
    # bracket annotation on the waste cell: primary -> sensitivity (DERIVED-inclusive)
    ax.text(1,-0.5-0.14,
            f"waste bracket: {wb['waste_primary_frac_wd']:.0%} \u2192 {wb['waste_sens_frac_wd']:.0%} of well-designed\n"
            f"({wb['waste_primary_n']}\u2192{wb['waste_sens_n']} trials; broadened def. counts independent citation)",
            ha="center",va="bottom",fontsize=6,color=DEVICE_C)
    ax.set_xticks([0,1]); ax.set_xticklabels(["results delivered","not delivered"])
    ax.set_yticks([0,1]); ax.set_yticklabels(["well-designed\n(RCT + powered)","weaker design"])
    ax.set_xlim(-0.5,1.5); ax.set_ylim(1.7,-0.7)
    ax.set_title(f"Design quality x evidentiary contribution — {condition}\nwaste = well-designed trials that never delivered (bracket = primary vs DERIVED-inclusive)",fontsize=7.5,loc="left")
    fig.savefig(outpath,dpi=200,bbox_inches="tight"); plt.close(fig)


def run_topic(condition, query, query_field="query.cond", scope="DRUG", terms=None,
              outdir="output", apply_style=None):
    d=os.path.join(outdir, f"CDQI_{slug(condition)}"); os.makedirs(os.path.join(d,"figures"),exist_ok=True)
    sg=slug(condition)
    qc=H.QCLog(f"CDQI_{sg}", outdir=d); dl=H.DecisionLog(f"CDQI_{sg}", outdir=d)
    dl.record("topic", f"condition='{condition}' query='{query}' field={query_field} scope={scope}")
    # 1. search + scope (ONE broad pull, reconciled inside fetch_studies)
    studies, universe, cr = search_and_scope(condition, query, query_field, scope, terms or [], qc, dl)
    assert len(studies)>0, f"no trials after scope for {condition}"
    # 2. checkpoint raw pull (never re-fetched)
    raw=[{"protocolSection":s.get("protocolSection"),"resultsSection":s.get("resultsSection"),
          "hasResults":s.get("hasResults")} for s in studies]
    with gzip.open(os.path.join(d,f"CDQI_{sg}_raw.json.gz"),"wt") as f: json.dump(raw,f)
    # 3. compute offline
    df=compute_matrix(studies); df.to_csv(os.path.join(d,f"CDQI_{sg}_dataset.csv"),index=False)
    # cross-type comparison (fig2 + supp1) is computed on the UNSCOPED universe, since a single
    # declared scope collapses int_class to one level. Everything else uses the scoped population.
    df_uni=compute_matrix(universe)
    t1=table1_cohort(df,condition); t1.to_csv(os.path.join(d,f"CDQI_{sg}_table1_cohort.csv"),index=False)
    t2=table2_components(df); t2.to_csv(os.path.join(d,f"CDQI_{sg}_table2_components.csv"),index=False)
    s1=supp_by_group(df_uni,"int_class"); s1.to_csv(os.path.join(d,f"CDQI_{sg}_supp1_by_intervention.csv"),index=False)
    s2=supp_by_group(df,"epoch",order=["<=2015","2016-2020","2021-2026"]); s2.to_csv(os.path.join(d,f"CDQI_{sg}_supp2_by_epoch.csv"),index=False)
    # 4. figures
    if apply_style: apply_style()
    fg=os.path.join(d,"figures")
    fig1_prisma(df,cr,condition,scope,os.path.join(fg,"fig1_prisma.png"))
    fig2_by_intervention(df_uni,condition,os.path.join(fg,"fig2_by_intervention.png"))
    fig3_epoch(df,condition,os.path.join(fg,"fig3_epoch_trend.png"))
    fig4_quality_contribution(df,condition,os.path.join(fg,"fig4_quality_contribution.png"))
    # 5. provenance + memo
    stamp=H.run_stamp(condition,{"query":query,"query_field":query_field,"scope":scope,
        "terms":terms or [],"n_scored":len(df),"completeness":cr.get("completeness")})
    json.dump(stamp,open(os.path.join(d,f"CDQI_{sg}_run_stamp.json"),"w"),indent=2)
    _write_memo(d,sg,condition,query,scope,df,t2,cr,stamp)
    dl.record("outputs_written", d)
    return dict(condition=condition, n=len(df), completeness=cr.get("completeness"),
                degenerate=cr.get("degenerate", False),
                stamp=stamp["stamp_hash"], outdir=d)


def _write_memo(d,sg,condition,query,scope,df,t2,cr,stamp):
    def row(c):
        r=t2[t2.component==COMP_LABEL[c]].iloc[0]; return f"{r.prevalence:.1%} [{r.ci_low:.1%}, {r.ci_high:.1%}] (n={int(r.n)})"
    if cr.get("completeness") is None:
        comp="n/a (see decision log)"
    elif cr.get("degenerate"):
        comp=f"{cr['completeness']:.0%} (degenerate — reflects unambiguous terminology, not a strong statistical estimate; §4.3)"
    else:
        comp=f"{cr['completeness']:.0%}"
    memo=f"""# CDQI data memo — {condition}

**Query:** `{query}`  |  **interventionType scope:** {scope}  |  **run-stamp:** `{stamp['stamp_hash']}`
**N scored trials:** {len(df)}  |  **search completeness estimate:** {comp}

Cite the run-stamp hash in the data-availability statement.

## Headline CDQI components (prevalence, Wilson 95% CI)
- Randomized (A1): {row('randomized')}
- Any blinding (A2): {row('blinded_any')}
- Double-blind+ (A2): {row('blinded_double_plus')}
- Meets power floor (A4): {row('power_ok')}
- Pivotal phase 3/4 (B1): {row('pivotal')}
- Results posted: {row('has_results')}
- Own publication linked: {row('has_result_ref')}

## Standing caveats (protocol §6)
- Read blinding WITHIN intervention type: procedure/device trials cannot blind the operator; a low
  double-blind rate there is structural, not a quality failure. See fig2 and supp1.
- Recent-epoch results-posting decline is a follow-up-time artifact (recent trials have not had time
  to report), not backsliding. See fig3.
- CDQI measures design AS DECLARED AT REGISTRATION; it complements — does not replace — RoB2/GRADE/Jadad.
- All proportions carry Wilson 95% CIs. CDQI is deterministic (structured fields only); no AI/human coding step.
"""
    open(os.path.join(d,f"CDQI_{sg}_data_memo.md"),"w").write(memo)


def main():
    ap=argparse.ArgumentParser(description="CDQI per-topic extraction engine")
    ap.add_argument("--condition",required=True); ap.add_argument("--query",required=True)
    ap.add_argument("--query-field",default="query.cond")
    ap.add_argument("--scope",default="DRUG",choices=list(SCOPE_TYPES))
    ap.add_argument("--terms",default="",help="comma-separated positive terms for capture-recapture (optional)")
    ap.add_argument("--outdir",default="output")
    a=ap.parse_args()
    r=run_topic(a.condition,a.query,a.query_field,a.scope,
                [t for t in a.terms.split(",") if t.strip()],a.outdir)
    print(f"Wrote package to: {r['outdir']}  (n={r['n']}, completeness={r['completeness']}, stamp={r['stamp']})")

if __name__=="__main__": main()
