# Decision Log — CDQI_total_knee_arthroplasty

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:10.841635+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='total knee arthroplasty' query='total knee arthroplasty' field=query.term scope=PROC_DEVICE

- **2026-07-20T18:32:15.709922+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.term='total knee arthroplasty' -> 2752 trials

- **2026-07-20T18:32:15.710054+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['knee', 'arthroplasty', 'knee', 'replacement', 'tka'] -> 1392 trials

- **2026-07-20T18:32:15.710098+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=2752 N_hat=2752.0 completeness=1.0

- **2026-07-20T18:32:15.710141+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 1412 scoped trials

- **2026-07-20T18:32:16.167312+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_total_knee_arthroplasty

- **2026-07-20T19:27:09.778189+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='total knee arthroplasty' query='total knee arthroplasty' field=query.term scope=PROC_DEVICE

- **2026-07-20T19:27:14.766096+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.term='total knee arthroplasty' -> 2752 trials

- **2026-07-20T19:27:14.766198+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['knee', 'arthroplasty', 'knee', 'replacement', 'tka'] -> 1392 trials

- **2026-07-20T19:27:14.766240+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=2752 N_hat=2752.0 completeness=1.0 degenerate=True

- **2026-07-20T19:27:14.766274+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 1412 scoped trials

- **2026-07-20T19:27:15.220536+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_total_knee_arthroplasty

- **2026-07-22T02:03:43.059008+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='total knee arthroplasty' query='total knee arthroplasty' field=query.term scope=PROC_DEVICE

- **2026-07-22T02:03:56.797160+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.term='total knee arthroplasty' -> 2753 trials

- **2026-07-22T02:03:56.797253+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['knee', 'arthroplasty', 'knee', 'replacement', 'tka'] -> 1393 trials

- **2026-07-22T02:03:56.797293+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=2753 N_hat=2753.0 completeness=1.0 degenerate=True

- **2026-07-22T02:03:56.797327+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 1413 scoped trials

- **2026-07-22T02:03:57.292261+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_total_knee_arthroplasty

