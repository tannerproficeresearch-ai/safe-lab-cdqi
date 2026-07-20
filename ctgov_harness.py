"""
ctgov_harness.py — SAFE Evidence Lab shared extraction + QC harness
===================================================================
Condition-agnostic core imported by every methodology (C, B, E).

Implements the SAFE Lab Verified Computational Study Workflow as CODE, so the
pipeline *emits* the evidence the Independent Reviewer needs on every run:

  * totalCount reconciliation ......... defeats Failure Mode #1 (silent API truncation)
  * QC checkpoint logging ............. row counts at every load / join / filter
  * append-only decision log .......... every analytic choice is recorded, timestamped
  * deterministic, re-runnable ........ fixed query params, no hidden state

--------------------------------------------------------------------------------
CRITICAL API BEHAVIOR (empirically verified against CT.gov API v2, this project)
--------------------------------------------------------------------------------
The website search bar and the API do NOT behave identically. Verified facts:

  1. `query.cond` is NOT exact-match. It runs the ClinicalTrials.gov "Essie"
     engine with tokenization + synonym/concept expansion.
       - query.cond=heart failure  -> 7731
       - query.cond=cardiac failure -> 7731  (synonym mapped to same concept)
       - query.cond=failure heart   -> 7728  (word order ~irrelevant; tokenized)

  2. QUOTING A TERM DISABLES concept expansion (forces exact phrase, NARROWER):
       - query.cond=chronic kidney disease      -> 5670  (expansion ON)
       - query.cond="chronic kidney disease"    -> fewer (expansion OFF)
     => Do NOT wrap the head condition in quotes unless you *want* exact phrase.

  3. Naive OR-combining with quotes can UNDER-count (it quotes each term):
       - chronic kidney disease                 -> 5670
       - "chronic kidney disease" OR CKD        -> 3810  (WORSE)
     => Only OR-combine to close a genuine ABBREVIATION gap, unquoted, and TEST it:
       - chronic hepatitis C                    -> 1506
       - chronic hepatitis C OR HCV             -> 2633  (+1127, real uplift)

  4. `query.term` is a whole-record search (title/desc/etc.) and returns a much
     larger, less specific set than `query.cond`. Use `query.cond` for a
     condition population; use `query.term` only for keyword probes.

REPRODUCIBILITY RULE FOR STUDENTS: record the EXACT query.cond string you ran
(see SEARCH_SPEC below / your protocol's Search Specification box). Registry
counts drift as trials are added, so your numbers will differ slightly from the
protocol's reference numbers — that is expected. What must match is the STRING.
"""

from __future__ import annotations
import urllib.request, urllib.parse, json, time, os, sys, hashlib, datetime
from typing import Iterator

API_V2 = "https://clinicaltrials.gov/api/v2"


# =============================================================================
# 1. LOW-LEVEL REQUEST with retry/backoff (transient proxy/network resilience)
# =============================================================================
def _request(path: str, params: dict, retries: int = 5, timeout: int = 60) -> dict:
    url = f"{API_V2}{path}?" + urllib.parse.urlencode(params)
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "safe-lab-harness"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:          # noqa: BLE001 — transient network/proxy
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"CT.gov request failed after {retries} tries: {url}\n  last error: {last}")


# =============================================================================
# 2. QC CHECKPOINT LOGGER  — SAFE Lab: row counts at every load/join/filter
# =============================================================================
class QCLog:
    """Append-only checkpoint recorder. Every count the Reviewer needs to see."""

    def __init__(self, study_id: str, outdir: str = "."):
        self.study_id = study_id
        self.path = os.path.join(outdir, f"{study_id}_qc_checkpoints.csv")
        self.rows: list[dict] = []
        self._write_header()

    def _write_header(self):
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                f.write("timestamp_utc,checkpoint,n_records,detail\n")

    def checkpoint(self, name: str, n: int, detail: str = ""):
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        detail = detail.replace(",", ";").replace("\n", " ")
        self.rows.append(dict(timestamp_utc=ts, checkpoint=name, n_records=n, detail=detail))
        with open(self.path, "a") as f:
            f.write(f"{ts},{name},{n},{detail}\n")
        print(f"[QC] {name:<28} n={n:<7} {detail}")
        return n


# =============================================================================
# 3. DECISION LOG  — SAFE Lab: append-only record of every analytic choice
# =============================================================================
class DecisionLog:
    """Every mid-session decision, timestamped and immutable once written."""

    def __init__(self, study_id: str, outdir: str = "."):
        self.path = os.path.join(outdir, f"{study_id}_decision_log.md")
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                f.write(f"# Decision Log — {study_id}\n\n"
                        f"Append-only. Each entry: what was decided, why, and by whom.\n\n")

    def record(self, decision: str, rationale: str, who: str = "Primary Analyst"):
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(self.path, "a") as f:
            f.write(f"- **{ts}** — *{who}*\n"
                    f"  - Decision: {decision}\n"
                    f"  - Rationale: {rationale}\n\n")
        print(f"[DECISION] {decision}")


# =============================================================================
# 4. THE CORE: reconciled, paginated fetch  — defeats silent truncation
# =============================================================================
def fetch_studies(query_cond: str,
                  qc: QCLog,
                  fields: list[str] | None = None,
                  status: list[str] | None = None,
                  advanced_filters: list[str] | None = None,
                  study_type: str | None = "INTERVENTIONAL",
                  page_size: int = 1000,
                  max_records: int | None = None,
                  query_field: str = "query.cond") -> list[dict]:
    """
    Fetch ALL studies for a condition and RECONCILE against the API's declared
    totalCount. Raises if the fetched count doesn't match what the API says
    exists — the single most important guard in the whole harness.

    query_cond : EXACT string for query.cond (see SEARCH_SPEC). Do NOT quote the
                 head term unless you intend to disable concept expansion.
    fields     : optional projection (list of API v2 field paths) to shrink payload.
    status     : optional list of overallStatus values (OR-combined by the API).
    advanced_filters : list of AREA[...] expressions, AND-combined.
    """
    adv = []
    if study_type:
        adv.append(f"AREA[StudyType]{study_type}")
    if advanced_filters:
        adv.extend(advanced_filters)

    # query_field lets procedure/device topics anchor on query.term or query.intr
    # (e.g. reverse shoulder arthroplasty is both a condition and an intervention);
    # defaults to query.cond for the drug/disease case.
    base = {query_field: query_cond, "pageSize": page_size,
            "countTotal": "true", "format": "json"}
    if adv:
        base["filter.advanced"] = " AND ".join(adv)
    if status:
        base["filter.overallStatus"] = "|".join(status)
    if fields:
        base["fields"] = ",".join(fields)

    out: list[dict] = []
    declared_total = None
    token = None
    while True:
        p = dict(base)
        if token:
            p["pageToken"] = token
        d = _request("/studies", p)
        if declared_total is None:
            declared_total = d.get("totalCount")
            qc.checkpoint("api_totalCount", declared_total,
                          f"{query_field}='{query_cond}'")
        out.extend(d.get("studies", []))
        token = d.get("nextPageToken")
        if not token or (max_records and len(out) >= max_records):
            break

    qc.checkpoint("records_fetched", len(out))

    # ---- RECONCILIATION (Failure Mode #1) ----
    if max_records is None and declared_total is not None and len(out) != declared_total:
        raise AssertionError(
            f"TRUNCATION GUARD TRIPPED: API declared totalCount={declared_total} "
            f"but fetched {len(out)} records. Do NOT trust downstream numbers. "
            f"Check pagination / nextPageToken handling before proceeding."
        )
    qc.checkpoint("reconciliation_ok", len(out),
                  f"fetched == totalCount ({declared_total})")
    return out


def get_count(query_cond: str, status: list[str] | None = None,
              advanced_filters: list[str] | None = None,
              study_type: str | None = "INTERVENTIONAL") -> int:
    """Cheap totalCount-only probe (pageSize=1). For yield checks / denominators."""
    adv = []
    if study_type:
        adv.append(f"AREA[StudyType]{study_type}")
    if advanced_filters:
        adv.extend(advanced_filters)
    p = {"query.cond": query_cond, "pageSize": 1, "countTotal": "true", "format": "json"}
    if adv:
        p["filter.advanced"] = " AND ".join(adv)
    if status:
        p["filter.overallStatus"] = "|".join(status)
    return _request("/studies", p).get("totalCount")


# =============================================================================
# 5. SAFE navigation + provenance stamp
# =============================================================================
def dig(d: dict, *path, default=None):
    """Safe nested-dict access: dig(study,'protocolSection','statusModule','overallStatus')."""
    cur = d
    for k in path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur


def run_stamp(query_cond: str, extra: dict | None = None) -> dict:
    """Deterministic provenance stamp saved alongside every dataset."""
    stamp = {
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "api": API_V2,
        "query_cond": query_cond,
        "python": sys.version.split()[0],
    }
    if extra:
        stamp.update(extra)
    stamp["stamp_hash"] = hashlib.sha256(
        json.dumps(stamp, sort_keys=True).encode()).hexdigest()[:12]
    return stamp


def capture_recapture(set_a, set_b):
    """Chapman (bias-corrected Lincoln-Petersen) estimate of true population size from
    two overlapping search strategies, each a set of NCT ids.

    Returns dict with n1, n2, overlap, union, N_hat (estimated true total),
    completeness (union / N_hat), and n_missed (estimated still-missed by both).

    Use to REPORT how complete a two-strategy search is, e.g.
        A = essie_phrase_ncts ; B = broadnet_classified_ncts
        cr = capture_recapture(A, B)
        -> state cr['completeness'] and cr['N_hat'] in the manuscript methods.
    """
    A, B = set(set_a), set(set_b)
    n1, n2, m = len(A), len(B), len(A & B)
    union = len(A | B)
    N_hat = ((n1 + 1) * (n2 + 1)) / (m + 1) - 1
    return {"n1": n1, "n2": n2, "overlap": m, "union": union,
            "N_hat": round(N_hat, 1),
            "completeness": round(union / N_hat, 4) if N_hat else None,
            "n_missed_est": round(N_hat - union, 1)}
