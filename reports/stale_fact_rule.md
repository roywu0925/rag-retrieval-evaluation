# Stale-fact measurement rule (pre-registered 2026-11-06, before any stale-fact answer exists)

This file defines how each generated answer to a stale-fact question is classified. The classifier is deterministic
string and number matching against patterns fixed in advance. **No LLM judge** is used, per the project constraint.
The rule and the per-fact patterns are frozen before the first stale-fact generation call (section 7). Nothing here is
tuned on stale-fact outputs.

Scope: facts SF1-SF11 in `eval/stale_facts.json`. X1 has its own rule (section 5).

Revision 3 (2026-11-06, Roy, before freeze): "original" added as a marker, with sensitivity line S2.

Revision 2 (2026-11-06, Roy, before any pattern file or answer existed): supersession markers narrowed;
denominator fixed; SF10/SF11 phrase lists made explicit; freeze order enforced; independent-interval overlap
replaced by a paired test with a power analysis; headline number under disagreement decided.

## 1. Per-fact patterns (`eval/stale_patterns.json`, written with the stale-fact questions, frozen before generation)

Each fact gets:
- `old`: regexes for the superseded value. For SF1 this includes the `also_old` values 0.17 and 0.25 yd.
- `current`: regexes for the current value.
- `scope_markers` (SF4 only): phrases that scope the week-1 table ("week 1", "first week", "week-1").

Numbers are matched after normalisation: commas, thousands separators and units are stripped, and numbers are
compared as decimals. Each fact's pattern states its tolerance explicitly. Example: SF2 `current` accepts any
p99 value in [76.2, 101.7] ms, or the range "76-102", and `old` is 68.9 exactly. Qualitative facts (SF9-SF11) use
the pre-registered key phrases below.

**SF10 (Tier 2 status) and SF11 (Task K status): explicit phrase lists.** These are case-insensitive and evaluated
per sentence. A topic regex must match in the same sentence as an `old` or `current` phrase.

| Fact | topic (same sentence) | `old` | `current` |
|---|---|---|---|
| SF10 | `\btier ?2\b` \| `streaming` \| `quanti[sz]` \| `serving` \| `latency` \| `\baws\b` \| `part 3` | `\bnot (yet )?(been )?(started\|begun)\b` \| `\bhas(n't\| not) (yet )?(started\|begun)\b` \| `\byet to (start\|begin)\b` | `sagemaker` \| `\bendpoint\b` \| `\bus-(west-2\|east-1)\b` \| `\bp(50\|95\|99)\b` \| `\b\d+(\.\d+)? ?ms\b` \| `\b(completed?\|finished\|done\|measured\|deployed\|benchmarked)\b` |
| SF11 | `task k` \| `learned[- ]model` \| `\bk[1-5]\b` \| `\bgru\b` | same as SF10 `old` | `\b(trained\|evaluated\|completed?\|finished\|done)\b` \| `\bk[1-5]\b.{0,60}\b\d+(\.\d+)? ?(yd\|yards)\b` |

For SF10 and SF11, an answer that matches both `old` and `current` (for example "Tier 2 has not started; the plan is
a SageMaker endpoint") is MIXED, which counts as propagated. This is the conservative direction.

Global list of `supersession_markers`: earlier, previously, originally, original, initially, first-pass, superseded,
corrected, revised, no longer, was later, replaced, retracted, removed, unsourced.
**Not markers:** "old", "week 1" and "week-1". For SF3, SF6 and SF7, "week 1" describes the old value rather than
flagging it. Counting it as a marker would turn PROPAGATED into OLD_FLAGGED, which biases toward the flattering
class. "Week 1" survives only as SF4's `scope_marker`.

## 2. Answer classes

Each answer is split into sentences at `.`, `;`, `。` and newline, but never inside a number. Each pattern match is
located in one sentence. Then:

| Class | Rule | Headline bucket |
|---|---|---|
| **CURRENT** | `current` matches and `old` does not match | current |
| **CURRENT_FLAGGED** | both match, and every sentence holding an `old` match also holds a supersession marker | current |
| **MIXED** | both match, and at least one `old` match sits in a sentence with no supersession marker | **propagated** |
| **PROPAGATED** | `old` matches, `current` does not, and there is no supersession marker in the old value's sentence | **propagated** |
| **OLD_FLAGGED** | `old` matches with a marker, and `current` does not match (the model knows it is stale but gives no replacement) | neither |
| **ABSTAIN** | neither matches, and the answer contains a pre-registered abstention phrase (full list in `abstention_phrases` of the pattern file, e.g. "not stated", "does not say", "cannot determine", "no information", "not in the provided") | neither |
| **OTHER** | neither matches and the answer does not abstain (a vague answer or a value from elsewhere) | neither |

Three headline buckets are reported:
- **propagated** = PROPAGATED + MIXED. MIXED counts as propagated because an unmarked old value is presented as
  true, and a reader cannot tell which value holds.
- **current** = CURRENT + CURRENT_FLAGGED.
- **neither** = OLD_FLAGGED + ABSTAIN + OTHER.

All seven classes are also reported. Two sensitivity lines are recomputed offline from the same answers:
- **S1**: MIXED moved to "neither".
- **S2**: reclassified with "original" removed from the supersession markers. "Original" was added in revision 3, and
  it sits close to the removed "week 1" case. Without it, "the original estimate was 51%" is PROPAGATED, not
  OLD_FLAGGED.

If either line changes the ordering of the mitigations within any arm, that change is **reported as a finding in the
main text**, not footnoted.

**SF4 (scoped, not superseded).** The week-1 table is not wrong, only scoped. Propagated means an `old` table value
with no `scope_marker` in its sentence and no statement that it is week-1 only. Current means a scoped value, or the
statement that full-data values move by under 0.3 yd with the ordering unchanged.

## 3. Retrieval-level measure, reported separately from the answer

For each stale-fact question and each config, the top-k chunks are mapped to corpus line ranges, and the question
is classified by which sites were retrieved:
- **old-only**: some `old_sites` line, no `current_sites` line.
- **current-only**: the reverse.
- **both**.
- **neither**.

This separates "retrieval fed the model the stale value" from "the model chose the stale value". The cross-tab of
retrieval class × answer bucket is the main stale-fact table. Site lines come from `eval/stale_facts.json`, which
was fixed at labelling time.

## 4. Rates, tests, and what is claimed

- **Unit:** one answer, which is one question × config × model arm × mitigation. The test unit is the **fact**:
  one question per fact per condition, n = 11 (SF1-SF11). Extra phrasings, if added, are reported descriptively
  and never enter the test.
- **Model arms:** Haiku 4.5, Sonnet 4.6, Opus 4.6, each reported separately.
- **Conditions (4):** baseline, exclude_context, recency_git, corrections_doc. 12 questions x 4 x 3 arms = 144 calls.
- **Rates.** The denominator is **all answers**, abstentions included:
  - propagation rate = propagated / all answers
  - current rate = current / all answers
  - **abstention rate** = ABSTAIN / all answers, reported next to the other two in every cell

  A model that abstains often must not look good on propagation. Every rate carries a Wilson 95% CI for
  description only.
- **Test of a mitigation.** The test is paired, because each fact is measured with and without the mitigation in
  the same arm.
  - Primary: **exact McNemar** (a two-sided binomial test on the discordant facts, "fixed" vs "broken").
  - Effect estimate: the paired difference in propagation rate, with a Newcombe (method 10) 95% CI for paired
    proportions.
  - Every result is shown as its 2×2 table (fixed / broken / stayed propagated / stayed not), per mitigation per arm.
  - Multiplicity: 3 mitigations per arm. Holm-adjusted p-values within an arm are reported next to unadjusted ones.
  - The earlier rule (two independent Wilson intervals must not overlap) is **dropped**. Overlapping intervals can
    coexist with a clearly non-zero difference, and that rule throws away the pairing.
- **What the design can detect** (`scripts/power_stale.py`, output in `logs/power_stale.txt`). This is exact
  enumeration, two-sided α = 0.05, 80% power. The MDE is the smallest detectable drop in propagation rate from
  baseline p0. Paired model: b = P(a fact not propagated at baseline becomes propagated under the mitigation).

  | n per cell | baseline p0 | Wilson overlap (old rule) | Fisher, unpaired | McNemar, b = 0 | McNemar, b = 0.1 |
  |---|---|---|---|---|---|
  | **11 (the design)** | 0.3 | not reachable | not reachable | not reachable | not reachable |
  | | 0.5 | not reachable | not reachable | not reachable | not reachable |
  | | 0.7 | −67 pts | −62 pts | −63 pts | not reachable |
  | | 0.9 | −71 pts | −63 pts | −63 pts | −65 pts |
  | 22 (optimistic*) | 0.5 | −46 | −41 | −34 | −43 |
  | | 0.7 | −53 | −46 | −34 | −40 |
  | 33 (optimistic*) | 0.5 | −40 | −35 | −23 | −32 |
  | | 0.7 | −44 | −36 | −23 | −29 |

  \*The n = 22 and n = 33 rows treat phrasings of the same fact as independent. They are not: phrasings are clustered
  within a fact, so these rows are upper bounds. They are shown only to say what more independent facts would buy.
  The corpus has 11 confirmed stale facts, so n is capped at 11.

  **Why n = 11 is this weak.** Exact McNemar at n = 11 rejects only if at least 6 facts are fixed and **none** are
  broken (6/0 gives p = 0.031; 5/0 gives p = 0.0625). If baseline propagation is 50% or lower, fewer than 6 facts are
  propagated to begin with, so no mitigation can reach significance, however well it works. With little within-fact
  correlation, pairing gains little over Fisher. Pairing pays off for smaller drops at larger n (the n = 33 rows).

  **Decision, made before running: mitigation results are descriptive by design.** Each mitigation is reported as
  its paired 2×2 table, the paired difference with its CI, and the McNemar p-value. A mitigation is called an
  effect only if McNemar rejects. Any other drop is reported as a direction, stated as "this design could not
  have detected it", not as "no effect". The one plausible large-effect case is excluding CONTEXT.md for the facts
  whose only old sites are in CONTEXT.md (SF5, SF10, SF11). Removing the old site there can remove the old value
  completely. That is reported per fact, not pooled.
- **Weak-vs-strong reading:** a mitigation failure is distinguished from a weak-model failure by comparing arms. A
  drop in propagation across all three arms is a mitigation effect. A drop only in the strongest arm is a capability
  effect. This is descriptive too. The three arms share the same 11 facts and are not independent replications.
- **Retrieval failures kept apart (Roy, 2026-11-06, fixed before any answer exists).** At baseline, retrieval returns
  ONLY old-value lines for **SF3, SF10 and SF11** (dry run, retrieval class "old-only"). For those three the model
  cannot answer correctly whatever it does, so propagation there is a retrieval failure, not a model failure. Every
  headline propagation rate is reported twice: over all 11 facts, and over the 8 facts excluding SF3, SF10 and
  SF11. The exclusion set is fixed by this baseline dry run and does not move with condition.
- **Noise floor.** No corrections chunk reaches top-5 for any question, so the `corrections_doc` prompts are
  identical to baseline. Those 36 answers are reported as baseline repeats, one set per arm: the count of answers
  that differ textually and the count that change class. That per-arm noise floor, together with the Haiku
  stability check (section 7), is printed next to every between-condition difference.
- **Recency.** Only `recency_git` is run. A second condition, `recency_content`, was meant to separate "the technique
  fails" from "the dates carry no information". It could not be built: the repo's whole history is a two-day
  publication burst, so no mechanical source of content dates exists. A `recency_git` failure therefore cannot be
  attributed to the technique, and is reported that way.
- **Per-fact view:** the marked facts (SF1-SF9, which carry inline correction markers) and the unmarked facts (SF10,
  SF11, which have no marker) are reported separately. Unmarked facts are the hard case by construction and should
  not be averaged with the rest.

## 5. X1 (hallucination probe)

The corpus names "the 0.23 lag figure" as corrected but gives neither its meaning nor its replacement:
- **CORRECT**: ABSTAIN-class wording, or a statement that the corpus does not give the replacement.
- **HALLUCINATED**: any asserted replacement value, unit, or meaning. This includes linking it to 0.77 yd, which
  the corpus never does.

## 6. Audit of the rule itself

The rule's error is measured, not assumed. Roy hand-labels into the seven classes:
- every answer classed MIXED, OLD_FLAGGED or OTHER (where string matching is most fragile), and
- a uniform random 20% of the rest (fixed seed, drawn after generation).

He labels blind to the rule's class.

**Headline number: the RULE's output, always.** Where Roy's hand labels disagree with the rule:
- the rule's classification is what enters every table and test;
- the disagreement rate (raw agreement, Cohen's κ, and the confusion matrix) is reported beside it;
- disagreements are not used to retune patterns for this run.

If agreement on the headline buckets is below 0.85, the rule's numbers are still the headline. They are labelled
"rule-dependent", and the hand-labelled rates for the audited subset are shown next to them.

## 7. Freeze order (enforced, not just intended)

The pre-registration is complete only when **both** hold: `eval/stale_patterns.json` exists, **and** no stale-fact
answer has been generated. The steps run in this order:
1. Write `eval/stale_patterns.json` together with the stale-fact questions.
2. Append to the freeze log below the UTC timestamp and the sha256 of `eval/stale_patterns.json` and of this file.
3. Only then generate. The stale-fact runner refuses to start if any of these hold:
   - the pattern file's sha256 differs from the logged value;
   - this file's sha256 differs from the logged value;
   - a stale-fact answer file already exists.

   Each answer record carries the pattern-file sha256 it was classified with.

**Stability check (Roy, 2026-11-06).** The baseline condition is run twice on one arm (Haiku 4.5, 24 calls) to
measure run-to-run noise, because temperature 0 without a seed is not guaranteed stable. It runs **after** the freeze
and before the main run, so no answer exists before the patterns are locked. Its answers go to
`logs/stale_stability.jsonl` and are never used as results. Its outcome (answers that differ at all, answers that
change class) is appended to the freeze log as a post-freeze entry. Every later between-condition difference is
reported next to this noise floor.

Freeze log:
- **FROZEN 2026-11-06T22:57:26Z.** No stale-fact answer existed at this time (neither logs/stale_answers.jsonl nor logs/stale_stability.jsonl).
  - `reports/stale_fact_rule.md` sha256 22fc89d2fc21437536d80f5ab02b2a847906b1b7531501bb9a24d6ff1dbb6ccd (body above this log)
  - `eval/stale_patterns.json` sha256 f8fb5425675919c0247362bfc2e30c0a6184f9ac7221052d9393596c0abeaf75
  - `eval/stale_facts.json` sha256 de1baed583c25a8917d717964d2c65ae5c6bd9ea2e3384751939fddc2b1f139c
  - `mitigations/stale_prompt.json` sha256 aa556f0937b4828c219a7318b423d28ec7455072f4480003f87153b1415002ef
  - `mitigations/recency_metadata.json` sha256 5daa5f171a87b96adda7c1e6ffee7b7f3771f30f557fa27b1dd358c8129d8216
  - `mitigations/CORRECTIONS.md` sha256 6c45f92a903a05a3369bde5f1e3152e627cfe59e5f04d09a7a93fba0d879697b
  - `indexes/corrections_titan-v2_cs512_ov100/vectors.npy` sha256 de3e3bc76e7cb6a2d9b61b4cd9f69b203d9255aacacccfa02d9b0b321fb2d4ab
  - `indexes/corrections_titan-v2_cs512_ov100/chunks.jsonl` sha256 90c0baae3d10ab1849a92310336c0714b62bf71539eb39271efe54e830deb1bf
  - `indexes/titan-v2_cs512_ov100/vectors.npy` sha256 7f808a225114215ded43c3c51d851a45ea7dd51b721d169fc0519f892db29e1e
  - `indexes/titan-v2_cs512_ov100/chunks.jsonl` sha256 57790dcfa11bf55bd9a5793e7f2069fe6f522c4bac011c41732360b4acda634e
  - `rag/stale_classify.py` sha256 86d0f88b48d7578754b7171162a12108092490ed17d1c63d6602ce24afef1b51
  - `scripts/run_stale.py` sha256 bfca8c024928a8d9b8ca7b79bae760618f96d8f5e8a023bbd8969fabb44a0518
- **POST-FREEZE 2026-11-06T22:58:14Z: stability check** (logs/stale_stability.jsonl, never results). Baseline, Haiku 4.5, run twice, 12 questions. Answers that differ textually: **0 of 12**. Answers that change class: **0 of 12**. Billed $0.0780. The noise floor for Sonnet 4.6 and Opus 4.6 comes from the corrections_doc baseline repeats in the main run.
- **POST-FREEZE 2026-11-06T23:31:45Z: hand-audit worksheets** (rule section 6), scripts/make_audit_worksheets.py. Shuffle seed **20261106** (numpy default_rng; one generator, worksheet 1 permuted first, then worksheet 2). The audit sample itself is the seed-0 draw already fixed by scripts/analyze_stale.py. Worksheet 1 = all 36 MIXED/OLD_FLAGGED/OTHER; worksheet 2 = the 22 random (18 fact answers + 4 X1, scored separately). Labels are the three headline buckets. Blank worksheets:
  - `reports/audit/worksheet_1.md` sha256 c21d9ba2126f2b13602dbd57a16d8e8e926c7248e94540e0279fd8306fdab154
  - `reports/audit/worksheet_2.md` sha256 d2018aa944580eb3ebb8209e5900f022aa6c337bd8cc8f92d885bf45badb11dc
  - `eval/stale_audit_worksheet_key.json` sha256 e295e9a8051e9bba90a4590712731e723bca22777c07741c78d5b003f57f8c69 (key; not for Roy)
