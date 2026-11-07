# Stale-fact answer audit: worksheet 1 of 2 (36 answers)

  

  

Do this one first.

  

  

## How to label

  

  

Each block shows a question, what the documentation **currently** says, what it **used to** say, and one

  

model answer. Decide what a reader of the answer would come away believing, and tick **exactly one** box by

  

changing `[ ]` to `[x]`.

  

  

- **propagated**: a reader of this answer would come away believing the superseded value is current.

  

- **current**: a reader would come away with the right value.

  

- **neither**: the answer gives neither value clearly, or declines to answer.

  

  

If none of the three fits, tick the closest and say why on the `Note:` line. Notes are read, not scored.

  

Some answers may look alike or repeat; label each one on its own. Fact, model and condition are hidden on

  

purpose. Please don't look them up.

  

  

---

  

  

### 1 of 36

  

  

Question: What fraction of tracks survive to the 3-second prediction horizon?

  

  

Current value: 3.5% (394 of 11,254 tracks, full data).

  

  

Superseded value: 4.6% (24 of 526 tracks, week 1).

  

  

Answer:

  

  

Only 3.5% of tracks survive to the 3-second horizon on the full 18-week dataset (394 of 11,254 tracks), while on the week 1 sample alone it was 4.6% (24 of 526 tracks).

  

  

Your label: [ ] propagated [ x] current [ ] neither

  

  

Note:

  

  

---

  

  

### 2 of 36

  

  

Question: What fraction of tracks survive to the 3-second prediction horizon?

  

  

Current value: 3.5% (394 of 11,254 tracks, full data).

  

  

Superseded value: 4.6% (24 of 526 tracks, week 1).

  

  

Answer:

  

  

At the 3-second prediction horizon, approximately **3.5%** of tracks survive (394 of 11,254 on the full 18-week dataset). On the week-1 sample alone, the figure was 4.6% (24 of 526 tracks).

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 3 of 36

  

  

Question: Has Tier 2 of the project (streaming, quantisation, latency, AWS) been carried out?

  

  

Current value: Tier 2 / Part 3 is complete: SageMaker endpoint latency was measured in us-west-2 and us-east-1.

  

  

Superseded value: Tier 2 "not started".

  

  

Answer:

  

  

According to the project's tier table, Tier 2 (Streaming, quantisation, latency, AWS) has status "not started." However, there is evidence that at least a partial serving-latency measurement was carried out: the REPRODUCING.md file describes a "Part 3" that includes local inference timing and mentions measurements against a live SageMaker endpoint, which overlaps with Tier 2's scope. The documentation does not indicate that Tier 2 was fully completed.

  

  

Your label: [ ] propagated [ ] current [ x] neither

  

  

Note:

  

  

---

  

  

### 4 of 36

  

  

Question: By player role, what is the mean prediction error of the velocity_turning_to_ball baseline for Defensive Coverage and for Targeted Receiver?

  

  

Current value: The table values are week-1 only; on the full 18 weeks every value moves by less than 0.3 yd and the ordering is unchanged.

  

  

Superseded value: The same week-1 values presented as if they were full-data values (no week-1 scope).

  

  

Answer:

  

  

According to the by-role breakdown, the `velocity_turning_to_ball` baseline has a mean prediction error of **2.707 yards** for Defensive Coverage and **1.174 yards** for Targeted Receiver. These figures are from Week 1 only, though when recomputed on the full 18 weeks, every value moves by less than 0.3 yards and the ordering is unchanged.

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 5 of 36

  

  

Question: Has Tier 2 of the project (streaming, quantisation, latency, AWS) been carried out?

  

  

Current value: Tier 2 / Part 3 is complete: SageMaker endpoint latency was measured in us-west-2 and us-east-1.

  

  

Superseded value: Tier 2 "not started".

  

  

Answer:

  

  

Based on the documentation, Tier 2 (streaming, quantisation, latency, AWS) has been only partially carried out. The status table marks it as "not started," but the reproducing instructions reference a script (`run_tier2b_phase1_local.py`) for local CPU inference timing that was completed, and latency measurements were taken against a live SageMaker endpoint — though those round-trip, region, batch-size, throughput, and cost numbers cannot be reproduced from the repository alone.

  

  

Your label: [ ] propagated [ ] current [ x] neither

  

  

Note:

  

  

---

  

  

### 6 of 36

  

  

Question: Has Tier 2 of the project (streaming, quantisation, latency, AWS) been carried out?

  

  

Current value: Tier 2 / Part 3 is complete: SageMaker endpoint latency was measured in us-west-2 and us-east-1.

  

  

Superseded value: Tier 2 "not started".

  

  

Answer:

  

  

No, Tier 2 has not been carried out. According to the documentation, Tier 2 (Streaming, quantisation, latency, AWS) has a status of "not started" and is estimated to require ~25 hours of effort. Only a partial local measurement for Part 3 of Tier 2 was completed, measuring CPU inference timing without AWS access.

  

  

Your label: [ x] propagated [ ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 7 of 36

  

  

Question: What fraction of tracks survive to the 3-second prediction horizon?

  

  

Current value: 3.5% (394 of 11,254 tracks, full data).

  

  

Superseded value: 4.6% (24 of 526 tracks, week 1).

  

  

Answer:

  

  

Only 3.5% of tracks survive to the 3-second horizon on the full 18-week dataset (394 of 11,254 tracks), while on the week 1 sample alone it was 4.6% (24 of 526 tracks).

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 8 of 36

  

  

Question: What fraction of tracks survive to the 3-second prediction horizon?

  

  

Current value: 3.5% (394 of 11,254 tracks, full data).

  

  

Superseded value: 4.6% (24 of 526 tracks, week 1).

  

  

Answer:

  

  

At the 3-second prediction horizon, only 3.5% of tracks survive on the full dataset (394 of 11,254 tracks), and 4.6% on week 1 alone (24 of 526 tracks). This low coverage is why the project's primary horizon was changed to 1.9 seconds, which has 53% coverage instead.

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 9 of 36

  

  

Question: By player role, what is the mean prediction error of the velocity_turning_to_ball baseline for Defensive Coverage and for Targeted Receiver?

  

  

Current value: The table values are week-1 only; on the full 18 weeks every value moves by less than 0.3 yd and the ordering is unchanged.

  

  

Superseded value: The same week-1 values presented as if they were full-data values (no week-1 scope).

  

  

Answer:

  

  

The `velocity_turning_to_ball` baseline has a mean prediction error of **2.707 yards** for Defensive Coverage and **1.174 yards** for Targeted Receiver. These figures are from week 1 only, though recomputed on the full 18 weeks every value moves by less than 0.3 yards and the ordering is unchanged.

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 10 of 36

  

  

Question: How much does knowing where the ball will land improve player-position prediction over constant velocity?

  

  

Current value: 0.31 yd at the 1.9 s primary horizon; 1.51 yd at 3 s (full 18 weeks).

  

  

Superseded value: About 0.9 yd (0.887 yd; week 1 only, 3 s horizon, 4.6% coverage).

  

  

Answer:

  

  

At the 3-second horizon, knowing the ball's landing spot (`toward_ball_land`) improves prediction by approximately 0.786 yards compared to `constant_velocity` (6.498 vs 7.284 yards error). However, this improvement is horizon-dependent: at the primary 1.9-second horizon across the full 18-week dataset, the destination information is worth only about 0.3 yards, growing to over 1.5 yards by 3 seconds. The documentation notes that this destination-only baseline achieves this gain with zero parameters fit to data, meaning the improvement comes purely from geometric information about where the ball will land.

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 11 of 36

  

  

Question: Has the learned-model part of Tier 1 (Task K) been done?

  

  

Current value: K1-K5 have been trained and evaluated.

  

  

Superseded value: Task K (the learned-model part) "not started".

  

  

Answer:

  

  

No, the learned-model part of Tier 1 (Task K) has not been done. According to the documentation, Task K is "not started" and Task P's cross-validation protocol must come first. The degradation study (Part 1) is complete, but the learned-model part (Part 2, Task K) remains pending.

  

  

Your label: [ x] propagated [ ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 12 of 36

  

  

Question: What fraction of tracks survive to the 3-second prediction horizon?

  

  

Current value: 3.5% (394 of 11,254 tracks, full data).

  

  

Superseded value: 4.6% (24 of 526 tracks, week 1).

  

  

Answer:

  

  

At the 3-second prediction horizon, only 3.5% of tracks survive on the full dataset (394 of 11,254 tracks), and 4.6% on week 1 alone (24 of 526 tracks). This low coverage is why the project's primary horizon was changed to 1.9 seconds, which has 53% coverage instead.

  

  

Your label: [ ] propagated [ x] current [ ] neither

  

  

Note:

  

  

---

  

  

### 13 of 36

  

  

Question: Has Tier 2 of the project (streaming, quantisation, latency, AWS) been carried out?

  

  

Current value: Tier 2 / Part 3 is complete: SageMaker endpoint latency was measured in us-west-2 and us-east-1.

  

  

Superseded value: Tier 2 "not started".

  

  

Answer:

  

  

Based on the documentation, Tier 2 has been partially completed. The local CPU inference floor measurement (run_tier2b_phase1_local.py) was executed, but the round-trip, region, batch-size, throughput, and cost measurements against a live SageMaker endpoint were measured against a live service and do not have a reproducible script. The latency and cost analysis has been performed and documented, but the full Tier 2 reproducible pipeline was not completed as a clone-and-run process.

  

  

Your label: [ ] propagated [ ] current [x ] neither

  

  

Note:

  

  

---

  

  

### 14 of 36

  

  

Question: Has the learned-model part of Tier 1 (Task K) been done?

  

  

Current value: K1-K5 have been trained and evaluated.

  

  

Superseded value: Task K (the learned-model part) "not started".

  

  

Answer:

  

  

No, the learned-model part of Tier 1 (Task K) has not been done. According to the documentation, Task K is "not started" and Task P's cross-validation protocol must come first. The degradation study (Part 1) is complete, but the learned-model part (Part 2, Task K) remains pending.

  

  

Your label: [ ] propagated [ ] current [x ] neither

  

  

Note:

  

  

---

  

  

### 15 of 36

  

  

Question: Has the learned-model part of Tier 1 (Task K) been done?

  

  

Current value: K1-K5 have been trained and evaluated.

  

  

Superseded value: Task K (the learned-model part) "not started".

  

  

Answer:

  

  

Based on the documentation, Task K (the learned model) has not been started as of the current state described. The documentation explicitly states that "Learned-model part (Task K) not started; Task P's CV protocol comes first," and that Task P (5-fold grouped cross-validation) must be completed before Task K. However, the repository layout and reproducing instructions do list scripts for Tasks K through M, suggesting they are planned but not yet executed.

  

  

Your label: [x ] propagated [ ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 16 of 36

  

  

Question: How much does knowing where the ball will land improve player-position prediction over constant velocity?

  

  

Current value: 0.31 yd at the 1.9 s primary horizon; 1.51 yd at 3 s (full 18 weeks).

  

  

Superseded value: About 0.9 yd (0.887 yd; week 1 only, 3 s horizon, 4.6% coverage).

  

  

Answer:

  

  

At the 3-second horizon, knowing the ball's landing spot (`toward_ball_land`) beats `constant_velocity` by about 0.79 yards (6.498 vs. 7.284 yd), and blending in momentum (`velocity_turning_to_ball`) pushes that advantage to about 0.89 yards (6.397 vs. 7.284 yd). However, this improvement is horizon-dependent: on the full 18-week dataset, the destination advantage is only ~0.3 yards at the primary 1.9-second horizon, growing past 1.5 yards by 3 seconds. The 3-second figures come from a thin sample (only 4.6% track coverage at that horizon in week 1), so the general answer depends heavily on how far out you are predicting.

  

  

Your label: [ ] propagated [ x] current [ ] neither

  

  

Note:

  

  

---

  

  

### 17 of 36

  

  

Question: What fraction of tracks survive to the 3-second prediction horizon?

  

  

Current value: 3.5% (394 of 11,254 tracks, full data).

  

  

Superseded value: 4.6% (24 of 526 tracks, week 1).

  

  

Answer:

  

  

At the 3-second prediction horizon, approximately 3.5% of tracks survive (394 of 11,254 on the full 18-week dataset). On the week-1 sample alone, the figure was 4.6% (24 of 526 tracks).

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 18 of 36

  

  

Question: Has Tier 2 of the project (streaming, quantisation, latency, AWS) been carried out?

  

  

Current value: Tier 2 / Part 3 is complete: SageMaker endpoint latency was measured in us-west-2 and us-east-1.

  

  

Superseded value: Tier 2 "not started".

  

  

Answer:

  

  

Based on the documentation, Tier 2 (streaming, quantisation, latency, AWS) has been only partially carried out. The status table in CONTEXT.md lists Tier 2 as "not started," but REPRODUCING.md references a `run_tier2b_phase1_local.py` script for local CPU inference timing of K3/K5/tbl_kalman_speed, and notes that round-trip, region, batch-size, throughput, and cost numbers were measured against a live SageMaker endpoint — though no reproducible script exists for that portion.

  

  

Your label: [ ] propagated [ ] current [ x] neither

  

  

Note:

  

  

---

  

  

### 19 of 36

  

  

Question: What fraction of tracks survive to the 3-second prediction horizon?

  

  

Current value: 3.5% (394 of 11,254 tracks, full data).

  

  

Superseded value: 4.6% (24 of 526 tracks, week 1).

  

  

Answer:

  

  

At the 3-second prediction horizon, approximately 3.5% of tracks survive (394 of 11,254 on the full 18-week dataset). On the smaller week-1 sample alone, the figure was 4.6% (24 of 526 tracks).

  

  

Your label: [ ] propagated [ x] current [ ] neither

  

  

Note:

  

  

---

  

  

### 20 of 36

  

  

Question: Has Tier 2 of the project (streaming, quantisation, latency, AWS) been carried out?

  

  

Current value: Tier 2 / Part 3 is complete: SageMaker endpoint latency was measured in us-west-2 and us-east-1.

  

  

Superseded value: Tier 2 "not started".

  

  

Answer:

  

  

Based on the documentation, Tier 2 (streaming, quantisation, latency, AWS) has been partially carried out. The CONTEXT.md table lists Tier 2 as "not started," but the REPRODUCING.md excerpts reference scripts for Part 3 latency measurements, including a local CPU inference timing script (`run_tier2b_phase1_local.py`) and round-trip/region/batch-size/throughput/cost numbers measured against a live SageMaker endpoint — though the latter cannot be reproduced from the repository alone.

  

  

Your label: [ ] propagated [ ] current [ x] neither

  

  

Note:

  

  

---

  

  

### 21 of 36

  

  

Question: Has the learned-model part of Tier 1 (Task K) been done?

  

  

Current value: K1-K5 have been trained and evaluated.

  

  

Superseded value: Task K (the learned-model part) "not started".

  

  

Answer:

  

  

Yes, the learned-model part of Tier 1 (Task K) has been done. Although the CONTEXT.md tier table states "Learned-model part (Task K) not started; Task P's CV protocol comes first," the more recently updated REPRODUCING.md (last updated 2026-11-03T16:46:29-08:00) lists completed scripts for Task P (`run_tier1_taskp.py`), Task K (`run_tier1_taskk.py` training K1/K2/K3), as well as K4 and K5 variants, along with leakage audits, degradation sweeps, and crossover bootstraps — indicating that the learned-model work was carried out after the CONTEXT.md tier table entry was written.

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 22 of 36

  

  

Question: Has the learned-model part of Tier 1 (Task K) been done?

  

  

Current value: K1-K5 have been trained and evaluated.

  

  

Superseded value: Task K (the learned-model part) "not started".

  

  

Answer:

  

  

Based on the documentation, Task K (the learned model) has not been started as of the current state described. The documentation explicitly states that "Learned-model part (Task K) not started; Task P's CV protocol comes first," and that Task P (5-fold grouped cross-validation) must be completed before Task K. However, the repository layout and reproducing instructions do list scripts for Tasks K through M, suggesting they are planned but not yet executed.

  

  

Your label: [ ] propagated [ x] current [ ] neither

  

  

Note:

  

  

---

  

  

### 23 of 36

  

  

Question: Has the learned-model part of Tier 1 (Task K) been done?

  

  

Current value: K1-K5 have been trained and evaluated.

  

  

Superseded value: Task K (the learned-model part) "not started".

  

  

Answer:

  

  

Yes, the learned-model part of Tier 1 (Task K) has been completed. The repository layout lists scripts for K1 through K5 training, degradation sweeps, leakage audits, and cross-validation comparison tables, and the reproducing instructions include concrete commands and measured runtimes for training all five model variants. The CONTEXT.md status note that "Learned-model part (Task K) not started; Task P's CV protocol comes first" was written before Part 2 was done, but the repository layout and reproducing sections document the full set of completed Task K scripts and their outputs.

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 24 of 36

  

  

Question: By player role, what is the mean prediction error of the velocity_turning_to_ball baseline for Defensive Coverage and for Targeted Receiver?

  

  

Current value: The table values are week-1 only; on the full 18 weeks every value moves by less than 0.3 yd and the ordering is unchanged.

  

  

Superseded value: The same week-1 values presented as if they were full-data values (no week-1 scope).

  

  

Answer:

  

  

The `velocity_turning_to_ball` baseline has a mean prediction error of **2.707 yards** for Defensive Coverage and **1.174 yards** for Targeted Receiver. These figures are from week 1 only, though recomputed on the full 18 weeks every value moves by less than 0.3 yards and the ordering is unchanged.

  

  

Your label: [ ] propagated [ x] current [ ] neither

  

  

Note:

  

  

---

  

  

### 25 of 36

  

  

Question: How much does knowing where the ball will land improve player-position prediction over constant velocity?

  

  

Current value: 0.31 yd at the 1.9 s primary horizon; 1.51 yd at 3 s (full 18 weeks).

  

  

Superseded value: About 0.9 yd (0.887 yd; week 1 only, 3 s horizon, 4.6% coverage).

  

  

Answer:

  

  

At the 3-second horizon, knowing the ball's landing spot (`toward_ball_land`) improves prediction by approximately 0.786 yards compared to `constant_velocity` (6.498 vs 7.284 yards error). However, this improvement is horizon-dependent: at the primary 1.9-second horizon across the full 18-week dataset, the destination information is worth only about 0.3 yards, growing to over 1.5 yards by 3 seconds. The documentation notes that this destination-only baseline achieves this gain with zero parameters fit to data, meaning the improvement comes purely from geometric information about where the ball will land.

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 26 of 36

  

  

Question: What fraction of tracks survive to the 3-second prediction horizon?

  

  

Current value: 3.5% (394 of 11,254 tracks, full data).

  

  

Superseded value: 4.6% (24 of 526 tracks, week 1).

  

  

Answer:

  

  

At the 3-second prediction horizon, approximately 3.5% of tracks survive (394 of 11,254 on the full 18-week dataset). On the smaller week-1 sample alone, the figure was 4.6% (24 of 526 tracks).

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 27 of 36

  

  

Question: What fraction of tracks survive to the 3-second prediction horizon?

  

  

Current value: 3.5% (394 of 11,254 tracks, full data).

  

  

Superseded value: 4.6% (24 of 526 tracks, week 1).

  

  

Answer:

  

  

At the 3-second prediction horizon, only 3.5% of tracks survive on the full dataset (394 of 11,254 tracks), and 4.6% on week 1 alone (24 of 526 tracks). This low coverage is why the project's primary horizon was changed to 1.9 seconds, which has 53% coverage instead.

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 28 of 36

  

  

Question: Has the learned-model part of Tier 1 (Task K) been done?

  

  

Current value: K1-K5 have been trained and evaluated.

  

  

Superseded value: Task K (the learned-model part) "not started".

  

  

Answer:

  

  

Based on the documentation, Task K (the learned model) had not been started as of the most recent update to CONTEXT.md, which states: "Learned-model part (Task K) not started; Task P's CV protocol comes first." However, the REPRODUCING.md file lists scripts for Tasks K, K4, and K5 (e.g., `run_tier1_taskk.py`, `run_tier1_taskk4.py`, `run_tier1_k5.py`), suggesting the infrastructure was written even if the task was not yet marked complete. The CONTEXT.md excerpt, being the more directly authoritative source on status, indicates Task K was still pending as of its last update.

  

  

Your label: [x ] propagated [ ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 29 of 36

  

  

Question: What fraction of tracks survive to the 3-second prediction horizon?

  

  

Current value: 3.5% (394 of 11,254 tracks, full data).

  

  

Superseded value: 4.6% (24 of 526 tracks, week 1).

  

  

Answer:

  

  

At the 3-second prediction horizon, only 3.5% of tracks remain (394 of 11,254 on the full dataset; it was 4.6%, 24 of 526, on week 1 alone). This low coverage is why the project's primary horizon was changed to 1.9 seconds, which has 53% coverage instead.

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 30 of 36

  

  

Question: Has Tier 2 of the project (streaming, quantisation, latency, AWS) been carried out?

  

  

Current value: Tier 2 / Part 3 is complete: SageMaker endpoint latency was measured in us-west-2 and us-east-1.

  

  

Superseded value: Tier 2 "not started".

  

  

Answer:

  

  

According to the CONTEXT.md tier table, Tier 2 (Streaming, quantisation, latency, AWS) has status "not started" with ~25 h of rough effort. However, the REPRODUCING.md file describes a "Part 3" that includes local inference timing and SageMaker endpoint latency measurements, which overlaps with Tier 2's scope — though it notes the full round-trip/region/batch-size/throughput/cost numbers required a live SageMaker endpoint and are not fully reproducible from the repository. So portions of the Tier 2 work appear to have been partially carried out (at least the local inference floor and some AWS serving-latency measurements), even though the tier table still lists it as "not started."

  

  

Your label: [ x] propagated [ ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 31 of 36

  

  

Question: What fraction of tracks survive to the 3-second prediction horizon?

  

  

Current value: 3.5% (394 of 11,254 tracks, full data).

  

  

Superseded value: 4.6% (24 of 526 tracks, week 1).

  

  

Answer:

  

  

Only 3.5% of tracks survive to the 3-second horizon on the full 18-week dataset (394 of 11,254 tracks), while on the week 1 sample alone it was 4.6% (24 of 526 tracks).

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---

  

  

### 32 of 36

  

  

Question: What fraction of tracks survive to the 3-second prediction horizon?

  

  

Current value: 3.5% (394 of 11,254 tracks, full data).

  

  

Superseded value: 4.6% (24 of 526 tracks, week 1).

  

  

Answer:

  

  

Only 3.5% of tracks survive to the 3-second horizon on the full 18-week dataset (394 of 11,254 tracks), while on the week 1 sample alone it was 4.6% (24 of 526 tracks).

  

  

Your label: [ ] propagated [ x] current [ ] neither

  

  

Note:

  

  

---

  

  

### 33 of 36

  

  

Question: Has Tier 2 of the project (streaming, quantisation, latency, AWS) been carried out?

  

  

Current value: Tier 2 / Part 3 is complete: SageMaker endpoint latency was measured in us-west-2 and us-east-1.

  

  

Superseded value: Tier 2 "not started".

  

  

Answer:

  

  

No, Tier 2 has not been carried out. According to the documentation, Tier 2 (Streaming, quantisation, latency, AWS) has a status of "not started" and is estimated to require ~25 hours of effort. Only a partial local measurement for Part 3 of Tier 2 was completed, measuring CPU inference timing without AWS access.

  

  

Your label: [ ] propagated [ ] current [ x] neither

  

  

Note:

  

  

---

  

  

### 34 of 36

  

  

Question: Has Tier 2 of the project (streaming, quantisation, latency, AWS) been carried out?

  

  

Current value: Tier 2 / Part 3 is complete: SageMaker endpoint latency was measured in us-west-2 and us-east-1.

  

  

Superseded value: Tier 2 "not started".

  

  

Answer:

  

  

According to the project's tier table, Tier 2 (Streaming, quantisation, latency, AWS) has status "not started." However, there is evidence that at least a partial local serving-latency measurement was carried out under a "Part 3" label, including a local inference timing script and measurements against a live SageMaker endpoint, though the full round-trip and cost numbers are not fully reproducible from the repository.

  

  

Your label: [ ] propagated [ ] current [x ] neither

  

  

Note:

  

  

---

  

  

### 35 of 36

  

  

Question: At sigma = 5, by what margin does IMM beat kalman_ca?

  

  

Current value: 58% (25.68 vs 40.62 yd, primary horizon).

  

  

Superseded value: 51% (39.37 vs 59.57, week 1, 3 s horizon).

  

  

Answer:

  

  

At σ = 5, IMM achieves 25.68 yd versus kalman_ca's 40.62 yd, a margin of approximately 14.94 yd, which represents a 58% improvement. This is noted as a larger margin than the original week-1 estimate suggested (39.37 vs. 59.57 yd, 51%).

  

  

Your label: [ ] propagated [ x] current [ ] neither

  

  

Note:

  

  

---

  

  

### 36 of 36

  

  

Question: By player role, what is the mean prediction error of the velocity_turning_to_ball baseline for Defensive Coverage and for Targeted Receiver?

  

  

Current value: The table values are week-1 only; on the full 18 weeks every value moves by less than 0.3 yd and the ordering is unchanged.

  

  

Superseded value: The same week-1 values presented as if they were full-data values (no week-1 scope).

  

  

Answer:

  

  

The `velocity_turning_to_ball` baseline has a mean prediction error of **2.707 yards** for Defensive Coverage and **1.174 yards** for Targeted Receiver. These figures are from week 1 only, and when recomputed on the full 18 weeks, every value moves by less than 0.3 yards with the ordering unchanged.

  

  

Your label: [ ] propagated [x ] current [ ] neither

  

  

Note:

  

  

---