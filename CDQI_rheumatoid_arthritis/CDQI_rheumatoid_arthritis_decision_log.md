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

