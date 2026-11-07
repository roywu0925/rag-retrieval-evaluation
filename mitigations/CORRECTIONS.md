# Corrections

Values this project has published and later corrected. Each entry gives the date of the correction, what was
superseded, what replaced it, and where the current value is written. Newest first.

- **2026-11-03 — per-role mean error table.** Superseded: week-1-only table. Replaced by: same table; full-18-week values move <0.3 yd, ordering unchanged. Current source: PART1_DETAIL.md.
- **2026-11-03 — which baselines invert the role split.** Superseded: every baseline except constant_acceleration and damped_velocity. Replaced by: every baseline except constant_acceleration, damped_velocity and constant_position. Current source: CONTEXT.md.
- **2026-11-03 — Tier 1 learned-model status (Task K).** Superseded: Learned-model part (Task K) not started. Replaced by: K1-K5 trained and evaluated. Current source: README.md.
- **2026-11-02 — NGS position accuracy.** Superseded: 0.15-0.30 yd "published range". Replaced by: no numeric spec published; measured stream quantized to 0.01 yd, no detectable noise above that step. Current source: PART1_DETAIL.md, CONTEXT.md, README.md.
- **2026-11-02 — serving p99 latency.** Superseded: 68.9 ms. Replaced by: 76-102 ms (76.2-101.7). Current source: README.md.
- **2026-11-02 — value of destination info (toward-ball vs constant_velocity gap).** Superseded: ~0.9 yd / 0.887 yd (week 1, 3s, 4.6% coverage). Replaced by: 0.31 yd @1.9s primary, 1.51 yd @3s (full 18 weeks). Current source: PART1_DETAIL.md.
- **2026-11-02 — lead noise-crossing sigma.** Superseded: 0.029 (week 1, 3s). Replaced by: 0.103 (floor) -> 0.147 (quadrature); headline now 0.075 (tbl_kalman_speed vs constant_velocity). Current source: PART1_DETAIL.md, CONTEXT.md, README.md.
- **2026-11-02 — 3s track coverage.** Superseded: 4.6% (24/526, week 1). Replaced by: 3.5% (394/11,254, full). Current source: CONTEXT.md, PART1_DETAIL.md.
- **2026-11-02 — IMM vs kalman_ca margin at sigma=5.** Superseded: 51% (39.37 vs 59.57, week 1, 3s). Replaced by: 58% (25.68 vs 40.62, primary horizon). Current source: PART1_DETAIL.md.
- **2026-11-02 — Tier 2A bottom line for K5.** Superseded: none of the four signals is deployment-ready. Replaced by: Signal 1 (input PSI) works for K5; claim holds for K3 only. Current source: TIER2A_RESULTS.md.
- **2026-11-02 — Tier 2 status (streaming, quantisation, latency, AWS).** Superseded: not started. Replaced by: Tier 2B / Part 3 completed: SageMaker endpoint measured in us-west-2 and us-east-1. Current source: README.md.
