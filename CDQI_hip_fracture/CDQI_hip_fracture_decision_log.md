# Decision Log — CDQI_hip_fracture

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:07.728797+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='hip fracture' query='hip fracture' field=query.cond scope=PROC_DEVICE

- **2026-07-20T18:32:10.454331+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='hip fracture' -> 812 trials

- **2026-07-20T18:32:10.454408+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['fixation', 'arthroplasty', 'nail', 'screw'] -> 271 trials

- **2026-07-20T18:32:10.454455+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=885 N_hat=1110.2 completeness=0.7971

- **2026-07-20T18:32:10.454495+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 490 scoped trials

- **2026-07-20T18:32:10.780804+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_hip_fracture

- **2026-07-20T19:27:07.416796+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='hip fracture' query='hip fracture' field=query.cond scope=PROC_DEVICE

- **2026-07-20T19:27:09.396891+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='hip fracture' -> 812 trials

- **2026-07-20T19:27:09.396981+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['fixation', 'arthroplasty', 'nail', 'screw'] -> 271 trials

- **2026-07-20T19:27:09.397033+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=885 N_hat=1110.2 completeness=0.7971 degenerate=False

- **2026-07-20T19:27:09.397074+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 490 scoped trials

- **2026-07-20T19:27:09.722595+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_hip_fracture

- **2026-07-22T02:03:37.309755+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='hip fracture' query='hip fracture' field=query.cond scope=PROC_DEVICE

- **2026-07-22T02:03:42.652415+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='hip fracture' -> 815 trials

- **2026-07-22T02:03:42.652517+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['fixation', 'arthroplasty', 'nail', 'screw'] -> 271 trials

- **2026-07-22T02:03:42.652571+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=888 N_hat=1114.3 completeness=0.7969 degenerate=False

- **2026-07-22T02:03:42.652617+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 493 scoped trials

- **2026-07-22T02:03:42.993317+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_hip_fracture



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

