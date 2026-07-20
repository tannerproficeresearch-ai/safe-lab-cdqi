# Decision Log — CDQI_low_back_pain

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:27.051043+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='low back pain' query='low back pain' field=query.cond scope=BEHAVIORAL

- **2026-07-20T18:32:34.679532+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='low back pain' -> 2781 trials

- **2026-07-20T18:32:34.679682+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['exercise', 'physical', 'therapy', 'injection'] -> 2992 trials

- **2026-07-20T18:32:34.679747+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=4100 N_hat=4973.0 completeness=0.8244

- **2026-07-20T18:32:34.679786+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=BEHAVIORAL types=['BEHAVIORAL'] -> 696 scoped trials

- **2026-07-20T18:32:35.117286+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_low_back_pain

