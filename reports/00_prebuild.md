# Pre-build report (nothing billed yet)

Snapshot: uwb-trajectory-degradation @ 9bfc7b16b097c282fd5f1cd906b83460e5cadb53 (2026-11-03), see corpus/SOURCE.txt.
Files: README, PART1_DETAIL, CONTEXT, TIER2A_RESULTS, REPRODUCING. No TIER*_SPEC.md files exist at this commit.

## Corpus size
33,757 tokens (tiktoken cl100k proxy; Titan/Cohere tokenizers differ by roughly 15%), 19,114 words.
PART1_DETAIL 14,306 | CONTEXT 8,160 | README 7,504 | REPRODUCING 3,078 | TIER2A 709

## Section-size distribution (tokens)
| split | n | min | median | p90 | max |
|---|---|---|---|---|---|
| H2 | 35 | 32 | 362 | 1,462 | 11,978 |
| H3 | 47 | 5 | 362 | 1,633 | 5,085 |
H2 in words: min 25 / median 229 / p90 800 / max 6,545.

The median section is about 362 tokens, so 256/512/1024 brackets it correctly: 256 splits a typical
section, 512 is about one section, 1024 merges sections. The distribution has a heavy tail, though:
PART1 "Results" (11,978) and CONTEXT "Current state" (5,988) hold 53% of all tokens.
Implications:
1. Gold labels must be at H3, not H2. An H2 gold label of PART1 "Results" covers 35% of the corpus.
2. Use heading-aware chunking (split at headings, then sub-split by token budget, prefix each chunk
   with its heading path). Otherwise 1024-token chunks fuse unrelated small sections.
3. Report a chance-level recall@k for each question, because gold sections vary in size about 1000x.

## Stale-fact cases: see eval/stale_facts.json
