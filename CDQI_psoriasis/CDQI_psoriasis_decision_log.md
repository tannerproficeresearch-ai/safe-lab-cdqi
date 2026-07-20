# Decision Log — CDQI_psoriasis

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:16.235725+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='psoriasis' query='psoriasis' field=query.cond scope=DRUG

- **2026-07-20T18:32:17.960011+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='psoriasis' -> 1899 trials

- **2026-07-20T18:32:17.960101+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=DRUG types=['DRUG'] -> 1460 scoped trials

- **2026-07-20T18:32:18.393410+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_psoriasis

- **2026-07-20T19:27:15.300553+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='psoriasis' query='psoriasis' field=query.cond scope=DRUG

- **2026-07-20T19:27:16.908099+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='psoriasis' -> 1899 trials

- **2026-07-20T19:27:16.908176+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: single-strategy (no positive-term list) -> degenerate completeness=1.0; reflects unambiguous terminology, not a strong statistical estimate (protocol §4.3)

- **2026-07-20T19:27:16.908235+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=DRUG types=['DRUG'] -> 1460 scoped trials

- **2026-07-20T19:27:17.393159+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_psoriasis

