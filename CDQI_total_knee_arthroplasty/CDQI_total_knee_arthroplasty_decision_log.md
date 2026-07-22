# Decision Log — CDQI_total_knee_arthroplasty

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:10.841635+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='total knee arthroplasty' query='total knee arthroplasty' field=query.term scope=PROC_DEVICE

- **2026-07-20T18:32:15.709922+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.term='total knee arthroplasty' -> 2752 trials

- **2026-07-20T18:32:15.710054+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['knee', 'arthroplasty', 'knee', 'replacement', 'tka'] -> 1392 trials

- **2026-07-20T18:32:15.710098+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=2752 N_hat=2752.0 completeness=1.0

- **2026-07-20T18:32:15.710141+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 1412 scoped trials

- **2026-07-20T18:32:16.167312+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_total_knee_arthroplasty

- **2026-07-20T19:27:09.778189+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='total knee arthroplasty' query='total knee arthroplasty' field=query.term scope=PROC_DEVICE

- **2026-07-20T19:27:14.766096+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.term='total knee arthroplasty' -> 2752 trials

- **2026-07-20T19:27:14.766198+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['knee', 'arthroplasty', 'knee', 'replacement', 'tka'] -> 1392 trials

- **2026-07-20T19:27:14.766240+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=2752 N_hat=2752.0 completeness=1.0 degenerate=True

- **2026-07-20T19:27:14.766274+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 1412 scoped trials

- **2026-07-20T19:27:15.220536+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_total_knee_arthroplasty

- **2026-07-22T02:03:43.059008+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='total knee arthroplasty' query='total knee arthroplasty' field=query.term scope=PROC_DEVICE

- **2026-07-22T02:03:56.797160+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.term='total knee arthroplasty' -> 2753 trials

- **2026-07-22T02:03:56.797253+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['knee', 'arthroplasty', 'knee', 'replacement', 'tka'] -> 1393 trials

- **2026-07-22T02:03:56.797293+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=2753 N_hat=2753.0 completeness=1.0 degenerate=True

- **2026-07-22T02:03:56.797327+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 1413 scoped trials

- **2026-07-22T02:03:57.292261+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_total_knee_arthroplasty



<!-- cdqi:missingness_and_benchmark_provenance -->
## Missing-data handling (provenance for the methods claim)

Recorded 2026-07-21 22:25 (offline provenance append; does NOT alter any extracted data).

Per-component denominator / missingness rule as applied by the extraction engine:
- Randomization (A1) and blinding (A2): a missing allocation/masking value is coded as the NEGATIVE
  category (not-randomized / not-blinded) and RETAINED in the denominator. Absence of a declared
  allocation is typically a single-group registration where randomization is legitimately absent.
- Power screen (A4): records with a missing enrollment count are DROPPED; the denominator is the
  non-missing-enrollment subset (reported as n in Table 2).
- Attrition (A3): computed on RESULTS-POSTED trials only (STARTED vs COMPLETED, participant flow);
  denominator = results-posted subset. The binary "acceptable attrition" uses a <20% threshold
  (Cochrane/RoB2 convention, pre-specified in OSF Amendment 1); the continuous rate is also reported.
- Comparator adequacy (A6): arm groups with missing/absent type are treated as NO comparator and
  retained in the denominator (consistent with single-group == no comparator).
- DMC oversight: reported among trials that STATE a DMC status; records with no DMC field are excluded
  from that component's denominator (reported as n in Table 2).
- IPD-sharing pledge: YES vs (NO / UNDECIDED / not-stated); the full distribution is in Table 1.
- interventionType (scope-critical): populated for ~99.8% of records (prereg §6.4).

This asymmetric handling (impute-negative-and-retain for A1/A2/A6 vs report-over-subset for A4/A3/DMC)
is intentional and is stated in the manuscript methods.

## Benchmark status (open manuscript task)

Scope-reconciled published comparators (protocol §8) are NOT YET sourced for the design/contribution
components, with ONE exception: the IPD-sharing pledge, benchmarked against the ClinicalTrials.gov
IPD-statement literature ("Primed to comply", PLOS One). Remaining comparators are to be sourced and
scope-reconciled (same study type, date window, registry, condition) at the manuscript stage.
Benchmarking is used for method validation and for contextual comparison in the Discussion; it does
NOT gate the results tables.

