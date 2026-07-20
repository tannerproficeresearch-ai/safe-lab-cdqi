# Decision Log — CDQI_inguinal_hernia

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:06.208710+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='inguinal hernia' query='inguinal hernia' field=query.cond scope=PROC_DEVICE

- **2026-07-20T18:32:07.376557+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='inguinal hernia' -> 512 trials

- **2026-07-20T18:32:07.376640+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['hernia', 'mesh', 'herniorrhaphy'] -> 302 trials

- **2026-07-20T18:32:07.376690+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=536 N_hat=556.1 completeness=0.9638

- **2026-07-20T18:32:07.376736+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=PROC_DEVICE types=['DEVICE', 'PROCEDURE'] -> 360 scoped trials

- **2026-07-20T18:32:07.682835+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_inguinal_hernia

