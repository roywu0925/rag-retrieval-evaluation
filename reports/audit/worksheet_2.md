Worksheet 2 of 2 (22 answers)
1 of 22
Question: Are any of the Tier 2A drift-monitoring signals deployment-ready for the K5 model?
Current value: Signal 1 (input PSI) works as a monitor for K5; "none is deployment-ready" holds for K3 only.
Superseded value: None of the four signals is deployment-ready.
Answer:
Yes. Signal 1 (input PSI) is deployment-ready for K5: it passes both the sensitivity and specificity metrics, with an alarm sigma of 0.091, a lead of +0.830 yd before K5's error crosses the best physics baseline, and quiet behavior (0.0272 vs. threshold 0.2) on the verified-benign shift. The one noted caveat—that K5's soft lead is thin (+0.069 yd)—is described as "not fatal," since the operationally relevant decision (whether to replace K5) is well covered.
Your label: [ ] propagated [x] current [ ] neither
Note:

2 of 22
Question: What is the position accuracy of the NFL Next Gen Stats player tracking data?
Current value: No numeric accuracy spec is published; the measured positions are quantised to 0.01 yd, with no detectable noise above that step.
Superseded value: A "published accuracy range" of 0.15-0.30 yd (also the uncited 0.17 yd and 0.25 yd figures).
Answer:
NFL Football Operations states only that the system "charts individual movements within inches" — it publishes no numeric accuracy figure. The project found that the published position stream is quantized to 0.01 yd, with no detectable white noise above that step. A previously cited range of 0.15–0.30 yd was fabricated and has been removed from the project.
Your label: [ ] propagated [x] current [ ] neither
Note:

3 of 22
Question: For which baseline predictors is Targeted Receiver error NOT lower than Defensive Coverage error?
Current value: constant_acceleration, damped_velocity AND constant_position.
Superseded value: Only constant_acceleration and damped_velocity.
Answer:
Based on the role-split table, the baseline predictors for which Targeted Receiver error is not lower than Defensive Coverage error are constant_acceleration, damped_velocity, and constant_position. For constant_acceleration, Targeted Receiver error (3.048) exceeds Defensive Coverage (2.921); for damped_velocity, Targeted Receiver (4.033) exceeds Defensive Coverage (3.565); and for constant_position, Targeted Receiver (8.545) exceeds Defensive Coverage (6.391). This is explicitly noted in the documentation, which states that every baseline except these inverts the pattern.
Your label: [ ] propagated [x] current [ ] neither
Note:

4 of 22
Question: The 0.23 lag figure was corrected. What was it corrected to?
Current value: The documentation does not say what the 0.23 figure was corrected to.
Superseded value: (none: nothing to supersede)
Answer:
The documentation provided does not say. The excerpts mention the 0.23 lag figure only as an example of an incorrect number that "existed in conversation and never in a file," but they do not state what it was corrected to.
Your label: [ ] invents a replacement [x] says it isn't given [ ] other
Note:

5 of 22
Question: What is the position accuracy of the NFL Next Gen Stats player tracking data?
Current value: No numeric accuracy spec is published; the measured positions are quantised to 0.01 yd, with no detectable noise above that step.
Superseded value: A "published accuracy range" of 0.15-0.30 yd (also the uncited 0.17 yd and 0.25 yd figures).
Answer:
The documentation provided does not say. NFL Football Operations states only that the system "charts individual movements within inches" without publishing a numeric accuracy figure. This project measured the published position stream directly and found it is quantized to 0.01 yd with no detectable white noise above that step, but does not specify an overall position accuracy figure.
Your label: [ ] propagated [x] current [ ] neither
Note:

6 of 22
Question: Are any of the Tier 2A drift-monitoring signals deployment-ready for the K5 model?
Current value: Signal 1 (input PSI) works as a monitor for K5; "none is deployment-ready" holds for K3 only.
Superseded value: None of the four signals is deployment-ready.
Answer:
Yes, Signal 1 (input PSI) is deployment-ready for the K5 model. It passes both sensitivity and specificity metrics, with an alarm sigma of 0.091 and a lead of +0.830 yards before K5's hard failure (crossing the best physics baseline), which is the operationally relevant threshold for deciding whether to replace K5.
Your label: [ ] propagated [x] current [ ] neither
Note:

7 of 22
Question: Has the learned-model part of Tier 1 (Task K) been done?
Current value: K1-K5 have been trained and evaluated.
Superseded value: Task K (the learned-model part) "not started".
Answer:
Yes, the learned-model part of Tier 1 (Task K) has been completed. According to the documentation, multiple scripts were run to train K1, K2, K3, K4, and K5 models across 5 folds each, with training times ranging from approximately 8 to 28 minutes per model. The results show that K5 (trained with noise augmentation) decisively outperformed the other variants on noisy data, while K3 performed best on clean data.
Your label: [ ] propagated [x] current [ ] neither
Note:

8 of 22
Question: The 0.23 lag figure was corrected. What was it corrected to?
Current value: The documentation does not say what the 0.23 figure was corrected to.
Superseded value: (none: nothing to supersede)
Answer:
The documentation provided does not say. The excerpts mention the 0.23 lag figure as an example of an incorrect number that "existed in conversation and never in a file," but they do not state what it was corrected to.
Your label: [ ] invents a replacement [x] says it isn't given [ ] other
Note:

9 of 22
Question: How much does knowing where the ball will land improve player-position prediction over constant velocity?
Current value: 0.31 yd at the 1.9 s primary horizon; 1.51 yd at 3 s (full 18 weeks).
Superseded value: About 0.9 yd (0.887 yd; week 1 only, 3 s horizon, 4.6% coverage).
Answer:
At the 3-second horizon, knowing the ball's landing spot (toward_ball_land) reduces error from 7.284 yards to 6.498 yards compared to constant_velocity — an improvement of about 0.8 yards — using no kinematic modelling at all. Blending destination with momentum (velocity_turning_to_ball) pushes this slightly further to 6.397 yards at 3s. However, the documentation notes this "destination is worth ~0.9 yd" figure is a far-horizon, thin-sample result; at the more representative median horizon of 1.9 seconds, the gain is only ~0.3 yards, growing past 1.5 yards by 3s on the full 18-week dataset.
Your label: [ ] propagated [x] current [ ] neither
Note:

10 of 22
Question: Has Tier 2 of the project (streaming, quantisation, latency, AWS) been carried out?
Current value: Tier 2 / Part 3 is complete: SageMaker endpoint latency was measured in us-west-2 and us-east-1.
Superseded value: Tier 2 "not started".
Answer:
Yes, Tier 2 has been largely carried out. The excerpts show detailed latency, batch-size, throughput, and cost measurements against a live SageMaker endpoint, as well as local inference timing via run_tier2b_phase1_local.py. However, the full round-trip latency table is not fully reproducible from the repository alone, since the SageMaker endpoint measurements are not clone-and-run.
Your label: [ ] propagated [x] current [ ] neither
Note:

11 of 22
Question: For which baseline predictors is Targeted Receiver error NOT lower than Defensive Coverage error?
Current value: constant_acceleration, damped_velocity AND constant_position.
Superseded value: Only constant_acceleration and damped_velocity.
Answer:
According to the documentation, constant_acceleration and damped_velocity are the baseline predictors where Targeted Receiver error is NOT lower than Defensive Coverage error. Additionally, constant_position also inverts this pattern (though this correction was noted as being made on 2026-11-03).
Your label: [ ] propagated [x] current [ ] neither
Note:

12 of 22
Question: The 0.23 lag figure was corrected. What was it corrected to?
Current value: The documentation does not say what the 0.23 figure was corrected to.
Superseded value: (none: nothing to supersede)
Answer:
The documentation provided does not say what the 0.23 lag figure was corrected to. The excerpts only mention that it was one of several incorrect numbers the project had to correct, and note that it "existed in conversation and never in a file," but they do not specify the corrected value.
Your label: [ ] invents a replacement [x] says it isn't given [ ] other
Note:

13 of 22
Question: How much does knowing where the ball will land improve player-position prediction over constant velocity?
Current value: 0.31 yd at the 1.9 s primary horizon; 1.51 yd at 3 s (full 18 weeks).
Superseded value: About 0.9 yd (0.887 yd; week 1 only, 3 s horizon, 4.6% coverage).
Answer:
Knowing the ball's landing point improves prediction over constant velocity by approximately 0.9 yards at the 3-second horizon on the week-1 sample (6.397 vs 7.284 yd for velocity_turning_to_ball vs constant_velocity). However, this gain is horizon-dependent: it is only about 0.3 yards at the primary 1.9-second median horizon and grows past 1.5 yards by 3 seconds on the full 18-week dataset. The destination information becomes the dominant signal at longer horizons, while contributing relatively little improvement at shorter ones.
Your label: [ ] propagated [x] current [ ] neither
Note:

14 of 22
Question: What is the p99 latency of the deployed SageMaker serving endpoint?
Current value: p99 latency is 76-102 ms (76.2-101.7 ms).
Superseded value: p99 latency is 68.9 ms.
Answer:
The p99 latency of the deployed SageMaker serving endpoint is 76–102 ms, measured across six rounds with batch size 22. This p99 latency sits on the budget line for a 10 Hz hard real-time loop rather than comfortably under it, with one round exceeding the 100 ms budget.
Your label: [ ] propagated [x] current [ ] neither
Note:

15 of 22
Question: At what position-noise sigma does the Kalman filter's error cross below constant_velocity's?
Current value: 0.103 yd (floor) -> 0.147 (quadrature); the headline crossing is now 0.075 (tbl_kalman_speed vs constant_velocity).
Superseded value: 0.029 (week 1, 3 s horizon).
Answer:
The tbl_kalman_speed error crosses below constant_velocity at σ = 0.075 yd under the quadrature convention and at σ = 0.028 yd under the floor convention. The plain kalman filter crosses later, at σ = 0.147 under quadrature and σ = 0.105 under floor.
Your label: [ ] propagated [x] current [ ] neither
Note:

16 of 22
Question: What is the p99 latency of the deployed SageMaker serving endpoint?
Current value: p99 latency is 76-102 ms (76.2-101.7 ms).
Superseded value: p99 latency is 68.9 ms.
Answer:
Based on the documentation, p99 latency is not a single fixed number. Across six rounds measured at batch 22, 40 seconds apart, p99 ranged from 76.2 ms to 101.7 ms (a 1.33× variation), with one round exceeding the 100 ms budget. An earlier single run had reported p99 as 68.9 ms, but this was noted to be the optimistic end of the range, not a representative value.
Your label: [ ] propagated [x] current [ ] neither
Note:

17 of 22
Question: The 0.23 lag figure was corrected. What was it corrected to?
Current value: The documentation does not say what the 0.23 figure was corrected to.
Superseded value: (none: nothing to supersede)
Answer:
The documentation provided does not say what the 0.23 lag figure was corrected to. It is mentioned only as one of several incorrect numbers that "existed in conversation and never in a file," but no replacement value is given in the excerpts.
Your label: [ ] invents a replacement [x] says it isn't given [ ] other
Note:

18 of 22
Question: For which baseline predictors is Targeted Receiver error NOT lower than Defensive Coverage error?
Current value: constant_acceleration, damped_velocity AND constant_position.
Superseded value: Only constant_acceleration and damped_velocity.
Answer:
Based on the results table broken down by role, the predictors for which Targeted Receiver error is not lower than Defensive Coverage error are constant_velocity (1.991 vs. 2.340 — receiver is actually better here, wait —) let me re-examine:
From the table:

constant_velocity: Defensive Coverage 2.340, Targeted Receiver 1.991 → Receiver IS lower

velocity_turning_to_ball: Defensive 2.707, Targeted 1.174 → Receiver IS lower

toward_ball_land: Defensive 3.310, Targeted 1.499 → Receiver IS lower

constant_acceleration: Defensive 2.921, Targeted 3.048 → Receiver is higher

damped_velocity: Defensive 3.565, Targeted 4.033 → Receiver is higher

constant_position: Defensive 6.391, Targeted 8.545 → Receiver is higher
The predictors for which Targeted Receiver error is not lower than Defensive Coverage error are constant_acceleration, damped_velocity, and constant_position — all three show higher error on the Targeted Receiver than on the Defensive Coverage
Your label: [ ] propagated [x] current [ ] neither
Note:

19 of 22
Question: How much does knowing where the ball will land improve player-position prediction over constant velocity?
Current value: 0.31 yd at the 1.9 s primary horizon; 1.51 yd at 3 s (full 18 weeks).
Superseded value: About 0.9 yd (0.887 yd; week 1 only, 3 s horizon, 4.6% coverage).
Answer:
Knowing the ball's landing point improves prediction over constant velocity by approximately 0.9 yards at the 3-second horizon on the week-1 sample (6.397 vs 7.284 yards), but this figure is horizon-dependent: on the full 18-week dataset the improvement is only ~0.3 yards at the primary 1.9-second horizon and grows past 1.5 yards by 3 seconds. The destination information becomes the dominant signal at longer horizons, while at shorter horizons current velocity alone is nearly as good or better.
Your label: [ ] propagated [x] current [ ] neither
Note:

20 of 22
Question: At sigma = 5, by what margin does IMM beat kalman_ca?
Current value: 58% (25.68 vs 40.62 yd, primary horizon).
Superseded value: 51% (39.37 vs 59.57, week 1, 3 s horizon).
Answer:
At σ=5, IMM (25.68 yd) beats kalman_ca (40.62 yd) by 58%.
Your label: [ ] propagated [x] current [ ] neither
Note:

21 of 22
Question: Has the learned-model part of Tier 1 (Task K) been done?
Current value: K1-K5 have been trained and evaluated.
Superseded value: Task K (the learned-model part) "not started".
Answer:
Yes, Task K has been done. The documentation describes scripts/run_tier1_taskk.py as the "shared training/checkpointing/eval code" that "trains K1, K2, K3" across 5 folds, with a measured runtime of approximately 28 minutes, and it is listed as a concrete step in the reproduction instructions. Additionally, the README reports detailed results from these models, including their performance comparisons and architectural details (single GRU layer, hidden size 64, 18,050 parameters).
Your label: [ ] propagated [x] current [ ] neither
Note:

22 of 22
Question: At sigma = 5, by what margin does IMM beat kalman_ca?
Current value: 58% (25.68 vs 40.62 yd, primary horizon).
Superseded value: 51% (39.37 vs 59.57, week 1, 3 s horizon).
Answer:
At σ=5, imm (25.68 yd) beats kalman_ca (40.62 yd) by 58%.
Your label: [ ] propagated [x] current [ ] neither
Note: