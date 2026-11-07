# Provenance of mitigations/CORRECTIONS.md (NOT indexed; this file never enters retrieval)

## Constraints (Roy, 2026-11-06)
1. Written as a real project would write one: a dated list of corrections in the project's voice. Each entry states
   what was superseded and what replaced it.
2. Written WITHOUT looking at the 12 stale-fact questions.
3. All 11 facts (SF1-SF11) covered at the same level of detail. No fact gets extra wording because its question is
   harder.

## How it was written
Every entry comes from ONE fixed template:
"**{date} — {quantity}.** Superseded: {old}. Replaced by: {current}. Current source: {files}."
The template is filled only from fields of `eval/stale_facts.json`:
- quantity, old, current: from that file;
- files: the file names in its current_sites.

Those fields were written on 2026-11-04/05, during corpus labelling. The stale-fact questions did not exist until
2026-11-06. No field was rewritten for wording or emphasis.

- **Date:** the latest `git blame --date=short` date at 9bfc7b1 of the lines in that fact's current_sites, in
  ~/Downloads/NFL.
- **Order:** newest first, ties in stale_facts.json order.
- **X1:** excluded. It is not a two-value fact, and the corpus gives no replacement to list.

**Edits to the source fields, all of them:**
- SF4 `current`: dropped the annotator note "(no full-data numbers given)".
- SF5 `current`: the field reads "...and constant_position as well", which is a continuation and not a sentence.
  It was expanded to the full statement "every baseline except constant_acceleration, damped_velocity and
  constant_position", with no added content.
- SF11 `current`: dropped the source pointer "(README Part 2, Headline results)", which is the job of the "Current
  source" column.
- SF1: `also_old` (0.17 yd and 0.25 yd) left out. No other fact has an `also_old` field, and including it would give
  SF1 extra wording.
- SF10 `current`: "Tier 2B / Part 3 completed: ..." is kept verbatim, although "Tier 2B" is the labeller's term.

## Whether constraint 2 was held: NOT in the strict sense
The author (Claude, this session) wrote the 12 questions earlier the same day, so they were in context while this
document was written. That cannot be undone. The mitigation is that no wording was authored freely: every entry is
the fixed template over fields that predate the questions, and every deviation is listed above. A strictly blind
version needs an author who has not seen `eval/stale_patterns.json`, either Roy or a fresh agent given only
stale_facts.json and this template.

## Equal detail (constraint 3)
- One template line per fact, with the same four parts.
- Entry lengths are 49-96 tokens (tiktoken proxy). The spread comes only from how long the source fields are:
  SF3 and SF6 have the longest `old`/`current` text.
- Whole document: 784 tokens.

## Direction of the bias (Roy, 2026-11-06): this condition likely UNDERSTATES a corrections document
The template keeps the source fields' terse shorthand ("@1.9s", "->", "Tier 2B"). That text is probably less
retrievable by a natural-language question than well-written prose would be, so retrieval reaches it less often.
The measured effect of `corrections_doc` is therefore a conservative estimate of what a corrections document can
do. This bias runs **against** the intervention, which is the safe direction for a claim that it helps. It is a
property of the design, chosen because every entry can be checked mechanically against fields that predate the
questions. Free prose would be more retrievable but could not be checked.
