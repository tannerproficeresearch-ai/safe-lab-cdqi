# Decision Log — CDQI_atrial_fibrillation

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:35.188943+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='atrial fibrillation' query='atrial fibrillation' field=query.cond scope=PROC_DEVICE

- **2026-07-20T18:32:40.812426+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='atrial fibrillation' -> 2607 trials

- **2026-07-20T18:32:40.812545+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['ablation', 'pvi', 'catheter'] -> 1166 trials

- **2026-07-20T18:32:40.812590+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=2701 N_hat=2835.5 completeness=0.9526

- **2026-07-20T18:32:40.812629+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 1556 scoped trials

- **2026-07-20T18:32:41.290333+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_atrial_fibrillation

- **2026-07-20T19:27:33.253362+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='atrial fibrillation' query='atrial fibrillation' field=query.cond scope=PROC_DEVICE

- **2026-07-20T19:27:39.029123+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='atrial fibrillation' -> 2607 trials

- **2026-07-20T19:27:39.029273+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['ablation', 'pvi', 'catheter'] -> 1166 trials

- **2026-07-20T19:27:39.029329+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=2701 N_hat=2835.5 completeness=0.9526 degenerate=False

- **2026-07-20T19:27:39.029366+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 1556 scoped trials

- **2026-07-20T19:27:39.498762+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_atrial_fibrillation

- **2026-07-22T02:04:45.446600+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='atrial fibrillation' query='atrial fibrillation' field=query.cond scope=PROC_DEVICE

- **2026-07-22T02:05:22.603555+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='atrial fibrillation' -> 2608 trials

- **2026-07-22T02:05:22.603850+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['ablation', 'pvi', 'catheter'] -> 1167 trials

- **2026-07-22T02:05:22.603908+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=2702 N_hat=2836.3 completeness=0.9526 degenerate=False

- **2026-07-22T02:05:22.603945+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 1556 scoped trials

- **2026-07-22T02:05:23.130309+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_atrial_fibrillation

