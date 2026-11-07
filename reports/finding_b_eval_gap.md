# The measured result: generated questions overstate retrieval quality, and the gap splits into style and language

Sources: reports/sweep_results.md, logs/sweep/base.jsonl. Scoring plan pre-registered 2026-11-05, before any retrieval.
Power analyses: scripts/power.py, power_rank.py, power_paired.py, all written before any data existed. Everything here
is **descriptive: point estimates with bootstrap 95% CIs, no hypothesis test.** The power analyses showed that a test
could not detect a gap of this size (below).

## The gap

Recall@5 at the base config (512 tokens, 8.2% measured overlap, top-5):

| set | n | recall@5 | MRR@5 | median rank |
|---|---|---|---|---|
| (1) Tier A main (Sonnet 4.6-generated, English, whole corpus) | 33 | 88 [76, 97] | 0.73 | 1 |
| (2) Tier B (Roy, verbatim Chinese), strict | 13 | 69 [46, 92] | 0.52 | 2 |
| (2) Tier B, lenient (differs only for multi-section B14) | 13 | 77 [54, 100] | 0.55 | 2 |
| (3) Tier A on the sections Tier B covers (main + top-up) | 27 | 100 [100, 100] | 0.87 | 1 |

- **Headline (pre-registered: (3) vs (2), the same sections):** generated questions retrieve their gold section
  **31 points more often** than Roy's [CI +8, +54] (strict), or 23 points [0, +46] (lenient).
- **Secondary, indicative only ((1) vs (2); the pools differ):** +19 [−7, +48].

**On the sections Tier B covers, every generated question was retrieved, and 31% of Roy's strict-scored questions
were not.** An eval set built only from generated questions would have reported this retriever as perfect on
exactly the sections a human user asks about.

## The decomposition: style and language, on the same facts

For each answerable Tier B question (R), Sonnet 4.6 wrote one question in Chinese (MC) and one in English (ME) on the
same gold section and fact. The generator saw the fact, never Roy's wording. After the pre-registered filters, 9
complete triads remain (11 R-ME pairs). Paired differences in recall@5, with bootstrap CIs:

| contrast | holds constant | n | difference |
|---|---|---|---|
| R − MC: **style** (human vs generated) | language (both Chinese) | 9 | −11 [−44, +22] |
| MC − ME: **language** (Chinese vs English) | style (both generated) | 9 | −11 [−33, 0] |
| R − ME: combined | none | 11 | **−27 [−55, 0]** |

On the 9 complete triads, the combined gap of −22 splits **evenly: about half style, about half language.** The
clearest single case is B01. Roy's question ranks the gold section 58th; both generated versions rank it 1st. The
upper limits of 0 in the CIs mean that **no pair goes the other way**: no generated question missed where Roy's hit.

Within-pair rank correlations are 0.00-0.15. The pre-registered paired power analysis needed about 0.9 for the
paired design to reach a 20-point bar. This confirms, in hindsight, that the paired test could not have been decisive.

## Why it is not a test, and what would make it one

- The pre-registered power analysis (Fisher, n = 28 vs 13) needed a true gap of **40-47 points** for 80% power. The
  observed ~27-31 sits below that. Rank-based tests needed 35-44 points, and the paired design needed a within-pair
  correlation of about 0.9. All three conclusions were written down before any retrieval ran.
- Detecting a 27-point gap needs **about 60 human questions per side.** Roy decided not to write more (2026-11-06).
  At that number they would no longer be questions he would naturally ask, which is what Tier B measures. The honest
  result is the point estimates, the intervals and the decomposition above.
- **The language part is a bias, not noise:** Tier B is Chinese and the corpus English, so more questions shrink the
  interval but not the language component. The style component is the part a larger human set would pin down.

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
- **B09 (underspecified premise: "why is K5 the best?"):** scored by Roy on the generated answers (best/pass/fail).
  **Pending.** The sheet is reports/audit/B09_worksheet.md.

## Caveats carried from pre-registration

- **Coverage:** Tier B's 13 answerable questions land on 8 gold sections (15 counting alternates). 30 of 46
  sections are never labelled, including most stale-fact sections. (3) controls for coverage; (1) vs (2) does not.
- **Two instrument fixes:** the evidence-quote matcher had three layout bugs (blockquote markers, wrap after "/",
  table-row pipes). Each was fixed generally, and all generated questions were re-filtered. 5 false drops were
  re-admitted after passing the verifier, and no other verdict changed. The verifier's positive control rejected
  6 of 6 should-fail questions.
