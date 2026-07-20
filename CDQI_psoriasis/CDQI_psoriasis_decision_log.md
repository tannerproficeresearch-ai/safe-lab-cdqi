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

