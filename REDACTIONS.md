# Redactions

This repository is published publicly. One after-the-fact edit was made to the
recorded artifacts. It is listed here so a reader can tell edited content from
original API output.

## R1 — AWS account identifiers in `probe/results.jsonl`

**Edited:** 2026-11-11, after the study was complete.

`probe/results.jsonl` holds the raw `AccessDeniedException` messages returned by
Bedrock during the model-availability investigation (see
`reports/operational_findings.md`). Those messages embed the calling principal's
ARN. Two values were replaced, across 5 lines:

| Original | Replaced with |
|---|---|
| the 12-digit AWS account ID | `<ACCOUNT_ID>` |
| the IAM user name | `<IAM_USER>` |

Nothing else in the file was altered. The error codes, model IDs, regions,
`input_type` values and line ordering are exactly as returned by the API.

**No credential was ever in this repository.** The working tree was scanned for
`AKIA`/`ASIA` access-key patterns, including inside `.npy` and `.sqlite` files:
zero matches. An AWS account ID is not itself confidential.

**Git history was deliberately not rewritten.** The pre-redaction values remain
readable in earlier commits. Rewriting history would change every commit hash
and break the provenance references elsewhere in this repository — a worse
trade than leaving a non-secret identifier in an old log.
