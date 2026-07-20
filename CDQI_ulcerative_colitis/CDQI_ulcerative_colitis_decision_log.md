# Decision Log — CDQI_ulcerative_colitis

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:18.454539+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='ulcerative colitis' query='ulcerative colitis' field=query.cond scope=DRUG

- **2026-07-20T18:32:20.054861+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='ulcerative colitis' -> 1292 trials

- **2026-07-20T18:32:20.055037+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=DRUG types=['DRUG'] -> 768 scoped trials

- **2026-07-20T18:32:20.420231+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_ulcerative_colitis

