# Decision Log — CDQI_atopic_dermatitis

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:31:54.060866+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='atopic dermatitis' query='atopic dermatitis' field=query.cond scope=DRUG

- **2026-07-20T18:31:55.464471+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='atopic dermatitis' -> 1427 trials

- **2026-07-20T18:31:55.464590+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=DRUG types=['DRUG'] -> 982 scoped trials

- **2026-07-20T18:31:55.848496+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_atopic_dermatitis

