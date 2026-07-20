# Decision Log — CDQI_major_depressive_disorder

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:23.361198+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='major depressive disorder' query='major depressive disorder' field=query.cond scope=DRUG

- **2026-07-20T18:32:26.488240+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='major depressive disorder' -> 3221 trials

- **2026-07-20T18:32:26.488495+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=DRUG types=['DRUG'] -> 1679 scoped trials

- **2026-07-20T18:32:26.981235+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_major_depressive_disorder

