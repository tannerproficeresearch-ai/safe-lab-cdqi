# Decision Log — CDQI_head_and_neck_cancer

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:31:55.900059+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='head and neck cancer' query='head and neck cancer' field=query.cond scope=DRUG

- **2026-07-20T18:32:02.386239+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='head and neck cancer' -> 6798 trials

- **2026-07-20T18:32:02.386408+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=DRUG types=['DRUG'] -> 4217 scoped trials

- **2026-07-20T18:32:03.228729+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_head_and_neck_cancer

- **2026-07-20T19:26:56.529167+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='head and neck cancer' query='head and neck cancer' field=query.cond scope=DRUG

- **2026-07-20T19:27:02.069380+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='head and neck cancer' -> 6798 trials

- **2026-07-20T19:27:02.069540+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: single-strategy (no positive-term list) -> degenerate completeness=1.0; reflects unambiguous terminology, not a strong statistical estimate (protocol §4.3)

- **2026-07-20T19:27:02.069607+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=DRUG types=['DRUG'] -> 4217 scoped trials

- **2026-07-20T19:27:02.916679+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_head_and_neck_cancer

