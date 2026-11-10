# The measured result: generated questions overstate retrieval quality, by somewhere between 9 and 58 points

Sources: reports/sweep_results.md, logs/sweep/base.jsonl. Scoring plan pre-registered 2026-11-05, before any retrieval.
Power analyses: scripts/power.py, power_rank.py, power_paired.py, all written before any data existed. Everything here
is **descriptive: point estimates with bootstrap 95% CIs, no hypothesis test.** The power analyses showed that a test
could not detect a gap of this size (below).

## The pre-registered comparison and its result

Recall@5 at the base config (512 tokens, 8.2% measured overlap, top-5):

| set | n | recall@5 [Wilson 95%] | MRR@5 | median rank |
|---|---|---|---|---|
| (1) Tier A main (Sonnet 4.6-generated, English, whole corpus) | 33 | 88 [73, 95] | 0.73 | 1 |
| (2) Tier B (Roy, verbatim Chinese), strict | 13 | 69 [42, 87] | 0.52 | 2 |
| (2) Tier B, lenient (differs only for multi-section B14) | 13 | 77 [50, 92] | 0.55 | 2 |
| (3) Tier A on the sections Tier B covers (main + top-up) | 27 | 100 [88, 100] | 0.87 | 1 |

- **Pre-registered headline: (3) vs (2), the same sections.** The gap is **somewhere between +9 and +58 points**
  (strict; Newcombe 95%; Fisher exact p = 0.008). The two ends support different conclusions, and this study cannot
  separate them. Lenient: +23 [+4, +50], p = 0.029.
- **Pre-registered secondary, indicative only ((1) vs (2); the pools differ in coverage):** +19 [−5, +46],
  p = 0.20. Not significant.

**Type M: the point estimate is likely larger than the true gap.** The design was pre-registered as underpowered: 40-47
points were needed for 80% power. A significant result from such a design is expected to be inflated, because only
the samples that land large clear the threshold.
- scripts/retrodesign_ab.py (output in logs/retrodesign_ab.txt) assumes generated questions near ceiling (true
  recall 0.97, as observed).

  | true gap | power | mean significant estimate | exaggeration |
  |---|---|---|---|
  | 5 | 0.04 | 26 | 5.1× |
  | 10 | 0.13 | 27 | 2.7× |
  | 15 | 0.27 | 29 | 1.9× |
  | 20 | 0.42 | 31 | 1.6× |
  | 30 | 0.70 | 37 | 1.2× |

- **An observed +31 is what this design returns whether the true gap is 5 or 20 points.** Quote the interval, not
  the +31.
- The retrodesign was written after the result. It quantifies the inflation and changes no pre-registered number.

The one robust observation: **on the sections Tier B covers, every generated question was retrieved, and 4 of Roy's
13 were not.** A generated-only eval set would have scored this retriever as perfect on exactly the sections a human
user asked about.

## Secondary: the paired decomposition (not a confirmation)

For each answerable Tier B question (R), Sonnet 4.6 wrote one question in Chinese (MC) and one in English (ME) on the
same gold section and fact. The generator saw the fact, never Roy's wording. This set was pre-registered as an
**addition** to the comparison above, explicitly not the primary one. After the pre-registered filters, 9 complete
triads remain (11 R-ME pairs).

| contrast (paired recall@5) | holds constant | n | hits (both / first only / second only / neither) | difference [Newcombe paired 95%] | exact McNemar |
|---|---|---|---|---|---|
| R − MC: style | language (both Chinese) | 9 | 6 / 1 / 2 / 0 | −11 [−47, +28] | p = 1.0 |
| MC − ME: language | style (both generated) | 9 | 8 / 0 / 1 / 0 | −11 [−43, +20] | p = 1.0 |
| R − ME: combined | none | 11 | 8 / 0 / 3 / 0 | −27 [−57, +4] | p = 0.25 |

**None is significant**, and the combined −27 must not be read as significant: its interval includes zero.
- **It does not confirm the headline.** The human side is the same set of questions: 11 of the 13 Tier B questions
  in set (2) are the R side here. Two cuts that share their human questions are the same data cut twice, not two
  measurements.
- **What it adds** is that on the 9 complete triads, the generated-vs-human difference splits about evenly between
  style and language (−11 and −11). There is no sign that the difference is purely one or the other. In 3 pairs the
  generated question hits where Roy's misses, and the reverse never happens.
- The clearest single case is B01. Roy's question ranks the gold section 58th; both generated versions rank it 1st.
- Within-pair rank correlations are 0.00-0.15. The pre-registered paired power analysis needed about 0.9 to reach
  a 20-point bar, so the paired test could not have been decisive.

## What would make it a test

- About **60 human questions per side** for a gap in this range: the pre-registered table gives 26 points at
  n = 60. Roy decided not to write more (2026-11-06). At that number they would no longer be questions he would
  naturally ask, which is what Tier B measures.
- **The language part is a bias, not noise:** Tier B is Chinese and the corpus English, so more questions shrink
  the interval but not the language component.

## Pre-registered special cases

- **B06 / B10, one sentence, two roles.** PART1 "Baselines" says "The first uses only the destination…".
  - That sentence is **B10's** correct answer. B10 is retrieved at rank 1-4 in every config. In 5 of 9 configs the
    answer cites PART1 "Results" rather than "Baselines": the retrieval is right and the citation is not.
  - The same sentence is **B06's** trap. B06 asks which method Roy used *first*, and the documents never say; "the
    first" in that sentence means first-named. The trap section is retrieved in 9 of 9 configs, and the model
    abstains in 9 of 9 (one in Chinese, which the English-only detector missed; see finding_a). **Retrieval reached
    the trap every time and the model did not fall for it**, under an explicit abstention instruction.
- **B02 (unanswerable: "why GRU and not transformer"):** abstains in 9 of 9. It does not take the predicted bait,
  the "18,050 parameters" passage.
- **B14 (multi-section):** strict 0/1 within top-5 (both groups covered only at rank 8), lenient 1/1 (rank 2). The
  strict-lenient gap is the shortcut route the pre-registration named.
- **B09 (underspecified premise: "why is K5 the best?"):** hand-scored by Roy against the pre-registered
  best/pass/fail rubric (reports/audit/B09_worksheet.md). **Base config: pass** (Roy's judgement). The answer ties K5's
  standing to noise-augmented training ("Does training under noise help? Yes, decisively") and otherwise says the
  documentation does not explain why. It accepts "K5 is the best" without the clean-data condition: it never says
  that K3 is best on clean data. The other 8 configs' answers were provided for reference and were not scored,
  so no cross-config B09 rate is reported. Retrieval ranks the gold section 1st in all 9 configs, so the miss is in
  the reading, not the retrieval.

## Caveats carried from pre-registration

- **Coverage:** Tier B's 13 answerable questions land on 8 gold sections (15 counting alternates). 30 of 46
  sections are never labelled, including most stale-fact sections. (3) controls for coverage; (1) vs (2) does not.
- **Two instrument fixes:** the evidence-quote matcher had three layout bugs (blockquote markers, wrap after "/",
  table-row pipes). Each was fixed generally, and all generated questions were re-filtered. 5 false drops were
  re-admitted after passing the verifier, and no other verdict changed. The verifier's positive control rejected
  6 of 6 should-fail questions.
