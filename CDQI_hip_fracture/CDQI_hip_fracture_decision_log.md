# Decision Log — CDQI_hip_fracture

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:07.728797+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='hip fracture' query='hip fracture' field=query.cond scope=PROC_DEVICE

- **2026-07-20T18:32:10.454331+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='hip fracture' -> 812 trials

- **2026-07-20T18:32:10.454408+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['fixation', 'arthroplasty', 'nail', 'screw'] -> 271 trials

- **2026-07-20T18:32:10.454455+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=885 N_hat=1110.2 completeness=0.7971

- **2026-07-20T18:32:10.454495+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 490 scoped trials

- **2026-07-20T18:32:10.780804+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_hip_fracture

