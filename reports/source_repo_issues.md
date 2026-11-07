# Issues found in the source repo (uwb-trajectory-degradation @ 9bfc7b1)
To fix in the repo after this project, NOT in the frozen corpus/ snapshot.

1. README.md, Part 2 — the learned models, prose after the variant table: "`velocity_turning_to_ball` is
   well-specified for targeted receivers (where K1/K2 do beat K3)" attributes velocity_turning_to_ball as the base
   for both K1 and K2. Both tables (README lines 75-76, and the Part 2 variant table) give K1's base as
   `tbl_kalman_speed`; only K2 uses `velocity_turning_to_ball`. Found while labelling Tier B Q5.
2. CONTEXT.md:93-94, tier status table: Tier 1 "Learned-model part (Task K) not started" and Tier 2 "not started"
   are both out of date; README Part 2 and Part 3 report the completed work. The table has no date, so a reader
   cannot tell it is out of date.
3. README.md:459 vs :474: the same initial GRU-vs-physics margin is "57%" at line 459 and "the 55%" at line 474.
4. Baseline count wording: "all 13 physics baselines" (README:426, also :241, :431, :441) vs "all 11 physics-only
   baselines" in the error_curves.png caption (README:194). These describe different sets: 13 = the 3 plotted
   plus the 10 in tier1_test_degrade_allbaselines; the 11 in the figure exclude the hybrids and include
   imm_resigma. State which set each sentence means.
5. README:472 ("at step 1 the model's error is 0.40 yd against the baseline's 0.04"): name the split and the
   baseline. No committed output holds these step-1 figures.
6. CV_CROSSING = 1.0552 and TEST_CROSSING = 0.9338 were hard-coded constants with no committed output.
   FIXED on branch regen-crossing-provenance (commit 706dfc9, not pushed): scripts/regen_crossing.py plus
   outputs/tier1_{cv,test}_crossing_regen.json and tier1_crossing_optimism.json. Both constants reproduce exactly.
   Follow-ups:
   - README:134 says "optimistic by 11%". The same-estimator value is 11.50%, which rounds to 12%, with a
     bootstrap 95% CI of 5.2-17.6%.
   - run_tier1_test_degrade.py:191 says the CV crossing was bootstrapped over "231 train+val games"; the CV
     play-level file contains 229 games.
7. README:364: "`ml.m5.large` ≈ $0.12/hr, so a 3-hour game ≈ $0.35". $0.12 x 3 = $0.36. The public list price
   is $0.115/hr (USW2-Host:ml.m5.large, AWS price list 2026-11-06), which gives $0.345 ≈ $0.35. The hourly price
   should cite its source, and the 3-hour game should be labelled an assumption. Billed rate not yet checked:
   Cost Explorer is denied for this IAM user.
8. README:305: "Moving the model ~4,000 km" has no derivation, and it does not verify. Great-circle distances:
   Oregon (Boardman) to Virginia (Ashburn) is about 3,500 km; the extra distance for the Vancouver client is
   about 3,300 km (Vancouver to Oregon 461 km, Vancouver to Virginia 3,750 km). AWS does not publish data-centre
   locations; Boardman and Ashburn are public reporting. +57 ms implies a fibre route about 1.7x the geodesic,
   which is plausible.
9. README:292 (DONE, uncommitted on branch regen-crossing-provenance): added that 0.8% is a lower bound (compute
   timed locally) and that endpoint ModelLatency bounds it from above at 9.11/36.61 ≈ 25%.

## Status as of 2026-11-05 (merged into main locally at 580350c, not pushed)
- 6: DONE. Both crossings regenerated and committed (706dfc9). README:134 now says "about 12% (11.5%; bootstrap 95%
  CI 5.2%-17.6%)", plus the CV CI and the 999/1000 valid draws (580350c).
- 6 follow-up, 231 vs 229: RESOLVED. Both are correct and count different things. 231 = train+val split
  (outputs/splits.json, 190+41; README:422 correct). 229 = games with at least one play reaching 1.9 s;
  2023091007 and 2023122407 have no play past 18 output frames. The wrong statement was the printout in
  run_tier1_test_degrade.py:191 (fixed). No number changes downstream.
- 9: DONE (580350c).
- 7 ($0.12/hr) and 8 (4,000 km): still open in the README. The resume now uses $0.35 and 3,500 km.
- 3, 4, 5: open, cleanup after this project.
Note: the eval corpus stays frozen at 9bfc7b1. These README changes are deliberately not in corpus/.
- 2026-11-06: 7 ($0.115/hr with price-list source and date) and 8 (~3,500 km with derivation) DONE in 6b0cb2b.
  main pushed to origin (9bfc7b1..6b0cb2b). Still open: 3, 4, 5. The eval corpus stays at 9bfc7b1 by design
  (corpus/SOURCE.txt), and the remote has now moved past it.
