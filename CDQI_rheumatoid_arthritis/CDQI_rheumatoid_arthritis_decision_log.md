# Decision Log — CDQI_rheumatoid_arthritis

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:20.475056+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='rheumatoid arthritis' query='rheumatoid arthritis' field=query.cond scope=DRUG

- **2026-07-20T18:32:22.815444+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='rheumatoid arthritis' -> 2543 trials

- **2026-07-20T18:32:22.815551+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=DRUG types=['DRUG'] -> 1616 scoped trials

- **2026-07-20T18:32:23.293883+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_rheumatoid_arthritis

- **2026-07-20T19:27:19.192647+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='rheumatoid arthritis' query='rheumatoid arthritis' field=query.cond scope=DRUG

- **2026-07-20T19:27:21.594724+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='rheumatoid arthritis' -> 2543 trials

- **2026-07-20T19:27:21.594846+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: single-strategy (no positive-term list) -> degenerate completeness=1.0; reflects unambiguous terminology, not a strong statistical estimate (protocol §4.3)

- **2026-07-20T19:27:21.594913+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=DRUG types=['DRUG'] -> 1616 scoped trials

- **2026-07-20T19:27:22.079847+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_rheumatoid_arthritis

- **2026-07-22T02:04:06.154094+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='rheumatoid arthritis' query='rheumatoid arthritis' field=query.cond scope=DRUG

- **2026-07-22T02:04:12.621372+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='rheumatoid arthritis' -> 2543 trials

- **2026-07-22T02:04:12.621466+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: single-strategy (no positive-term list) -> degenerate completeness=1.0; reflects unambiguous terminology, not a strong statistical estimate (protocol §4.3)

- **2026-07-22T02:04:12.621523+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=DRUG types=['DRUG'] -> 1616 scoped trials

- **2026-07-22T02:04:13.233948+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_rheumatoid_arthritis



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

