# Decision Log — CDQI_inguinal_hernia

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:06.208710+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='inguinal hernia' query='inguinal hernia' field=query.cond scope=PROC_DEVICE

- **2026-07-20T18:32:07.376557+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='inguinal hernia' -> 512 trials

- **2026-07-20T18:32:07.376640+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['hernia', 'mesh', 'herniorrhaphy'] -> 302 trials

- **2026-07-20T18:32:07.376690+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=536 N_hat=556.1 completeness=0.9638

- **2026-07-20T18:32:07.376736+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 360 scoped trials

- **2026-07-20T18:32:07.682835+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_inguinal_hernia

- **2026-07-20T19:27:05.973762+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='inguinal hernia' query='inguinal hernia' field=query.cond scope=PROC_DEVICE

- **2026-07-20T19:27:07.065437+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='inguinal hernia' -> 512 trials

- **2026-07-20T19:27:07.065524+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['hernia', 'mesh', 'herniorrhaphy'] -> 302 trials

- **2026-07-20T19:27:07.065586+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=536 N_hat=556.1 completeness=0.9638 degenerate=False

- **2026-07-20T19:27:07.065634+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 360 scoped trials

- **2026-07-20T19:27:07.369041+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_inguinal_hernia

- **2026-07-22T01:48:45.346978+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='inguinal hernia' query='inguinal hernia' field=query.cond scope=PROC_DEVICE

- **2026-07-22T01:48:49.087505+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='inguinal hernia' -> 512 trials

- **2026-07-22T01:48:49.087574+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['hernia', 'mesh', 'herniorrhaphy'] -> 302 trials

- **2026-07-22T01:48:49.087628+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=536 N_hat=556.1 completeness=0.9638 degenerate=False

- **2026-07-22T01:48:49.087674+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 360 scoped trials

- **2026-07-22T01:48:49.450588+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_inguinal_hernia

- **2026-07-22T02:03:34.514468+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='inguinal hernia' query='inguinal hernia' field=query.cond scope=PROC_DEVICE

- **2026-07-22T02:03:36.943770+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='inguinal hernia' -> 512 trials

- **2026-07-22T02:03:36.943853+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['hernia', 'mesh', 'herniorrhaphy'] -> 302 trials

- **2026-07-22T02:03:36.943904+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=536 N_hat=556.1 completeness=0.9638 degenerate=False

- **2026-07-22T02:03:36.943954+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 360 scoped trials

- **2026-07-22T02:03:37.262945+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_inguinal_hernia



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

