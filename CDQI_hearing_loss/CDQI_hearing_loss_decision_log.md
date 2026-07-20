# Decision Log — CDQI_hearing_loss

Append-only. Each entry: what was decided, why, and by whom.

- **2026-07-20T18:32:03.337160+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='hearing loss' query='hearing loss' field=query.cond scope=DEVICE

- **2026-07-20T18:32:05.832500+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='hearing loss' -> 1085 trials

- **2026-07-20T18:32:05.832566+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['cochlear', 'hearing', 'aid', 'implant'] -> 816 trials

- **2026-07-20T18:32:05.832605+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=1217 N_hat=1294.3 completeness=0.9403

- **2026-07-20T18:32:05.832641+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=DEVICE types=['DEVICE'] -> 553 scoped trials

- **2026-07-20T18:32:06.153913+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_hearing_loss

- **2026-07-20T19:27:03.045072+00:00** — *Primary Analyst*
  - Decision: topic
  - Rationale: condition='hearing loss' query='hearing loss' field=query.cond scope=DEVICE

- **2026-07-20T19:27:05.599645+00:00** — *Primary Analyst*
  - Decision: search_strategy_A
  - Rationale: query.cond='hearing loss' -> 1085 trials

- **2026-07-20T19:27:05.599738+00:00** — *Primary Analyst*
  - Decision: search_strategy_B
  - Rationale: broad query.term + classify terms=['cochlear', 'hearing', 'aid', 'implant'] -> 816 trials

- **2026-07-20T19:27:05.599797+00:00** — *Primary Analyst*
  - Decision: capture_recapture
  - Rationale: union=1217 N_hat=1294.3 completeness=0.9403 degenerate=False

- **2026-07-20T19:27:05.599837+00:00** — *Primary Analyst*
  - Decision: intervention_scope
  - Rationale: scope=DEVICE types=['DEVICE'] -> 553 scoped trials

- **2026-07-20T19:27:05.923721+00:00** — *Primary Analyst*
  - Decision: outputs_written
  - Rationale: output/CDQI_hearing_loss

