# Operational findings

## OF1: Cohere access failed partway through the day. Cross-region routing is not the explanation (2026-11-04)

Source: probe/results.jsonl. The request bodies were identical across calls, from the same IAM identity.

| # | model | route | result |
|---|---|---|---|
| 1 | cohere.embed-english-v3 | in-region | worked earlier in the day (user measured norm 0.999951) |
| 2 | us.cohere.embed-v4:0 | cross-region profile | 5 calls denied on bedrock:InvokeModel for `arn:aws:bedrock:us-east-1::foundation-model/cohere.embed-v4:0` (served from us-east-1) |
| 3 | (IAM policy edited: foundation-model/* and inference-profile/* resources) | | |
| 4 | us.cohere.embed-v4:0 | cross-region profile | 2303-char doc + query both succeeded (norm 1.000000, 503 billed tokens) |
| 5 | us.cohere.embed-v4:0 | cross-region profile | 5997-char doc + query and bad-input-type: Marketplace entitlement error |
| 6 | us.cohere.embed-v4:0 | cross-region profile | identical 2303-char request from #4: Marketplace entitlement error |
| 7 | cohere.embed-english-v3 | **in-region** | doc + query + bad-input-type: **the same** Marketplace entitlement error |

Error text (#5-#7): "Model access is denied due to IAM user or service role is not authorized to perform the
required AWS Marketplace actions (aws-marketplace:ViewSubscriptions, aws-marketplace:Subscribe) ... If you recently
fixed this issue, try again after 5 minutes."

**What changed in our reading after #7.** After #6, the evidence fit two explanations: per-call routing to a region
without the entitlement, or a state change. #7 is a model with no cross-region routing failing the same way. So
routing is not needed to explain the failures. An account-level Marketplace entitlement state for Cohere, which
changed during the day, explains #4-#7 together. The confirmed facts about routing still stand: a us-west-2 request
was authorized against a us-east-1 resource (#2), and no response header names the serving region, so the client
cannot attribute a failure to a region.

**Not yet isolated.** What flipped the entitlement. The one known change between the working v3 call (#1) and the
failures is the IAM edit (#3). Whether that edit removed Marketplace permissions that #1 relied on can be checked in
the policy's version history. That check is free and has not been done.

**Lesson for a measurement study.** Authorization for third-party Bedrock models depends on Marketplace
entitlement state as well as IAM. That state can change without any request change and fails at call time. A sweep
can lose runs this way, so each model needs a fresh access check right before its runs, not one at setup.

Profile latency (v4) is not comparable with in-region latency and would be reported in its own row.

**Server-side evidence found afterwards (free API, `bedrock:GetFoundationModelAvailability`).**

| model | agreement | authorization | entitlement | region |
|---|---|---|---|---|
| cohere.embed-english-v3 | **NOT_AVAILABLE** | AUTHORIZED | AVAILABLE | AVAILABLE |
| cohere.embed-v4:0 | **NOT_AVAILABLE** | AUTHORIZED | AVAILABLE | AVAILABLE |
| anthropic.claude-sonnet-5-5 / sonnet-5 / haiku-5-5 / haiku-4-5 | **NOT_AVAILABLE** | AUTHORIZED | AVAILABLE | AVAILABLE |
| amazon.titan-embed-text-v2:0 | AVAILABLE | AUTHORIZED | AVAILABLE | AVAILABLE |
| amazon.nova-pro / nova-lite / nova-2-lite | AVAILABLE | AUTHORIZED | AVAILABLE | AVAILABLE |

Every third-party (Marketplace-sold) model shows no accepted model-access agreement, and every first-party Amazon
model shows one. The Claude statuses were unchanged when re-checked on 2026-11-05.

**RESOLVED 2026-11-06. See OF3: the blocker was Marketplace permissions, not the agreement.** The paragraph below is
kept as it was written on 2026-11-05.

**(Superseded) UNRESOLVED: this does not explain the Cohere failures.** It is contradicted by successful Cohere calls on the
same account: two v4 calls in our own log (#4, doc + query, real 1024-dim vectors returned) and the user's v3
measurement (#1, not in our log). Either access existed then and was lost, or calls can succeed while the agreement
reads NOT_AVAILABLE. The first of those is a state change, which this finding already could not isolate. The second
would mean the status field is not the gate it appears to be. The data cannot separate them, for two reasons: the
status was first checked after every failure had already happened, and the probe log records no timestamps.
**No cause is asserted for the Cohere failures.** The agreement status is recorded as one observation alongside the
others.

**Lesson, revised.** Record model availability status, with timestamps, before and after every run on a third-party
Bedrock model, not only IAM. A successful call does not show access is stable, and on this account a NOT_AVAILABLE
status did not mean calls would fail.

**Outcome.** The model axis was cut (2026-11-04). The study runs on Titan v2 only, which is first-party, in-region, and
needs no Marketplace entitlement. Losing a planned experimental axis to authorization state is the measured
cost of this failure mode. That is the reason it is recorded here.

## OF2: numpy warnings on the cosine were a false alarm; the arithmetic was checked independently

The v4 probe's cosine line emitted divide-by-zero, overflow and invalid-value RuntimeWarnings, while the norm
computed cleanly. First hypothesis: a reduced-precision dtype overflowing a 1024-dim dot product. Ruled out:
- The request asks only for `embedding_types: ["float"]`. The JSON values are Python floats, converted to float64.
- The same three warnings reproduce on random float64 unit vectors with no API data
  (numpy 2.0.2, macOS 26.6, arm64), and the result still matches `math.fsum` exact summation to 1e-16.
  This is a known numpy 2.0.x false alarm on Apple Silicon: the macOS BLAS library raises floating-point flags spuriously.

So the warning was real and the arithmetic was correct. The probe now computes every cosine both ways (exact fsum
and numpy) and prints the difference.

The v4 value itself (0.969933) was never confirmed. Its vectors were not saved, and every re-run failed on
authorization (OF1). It is not used anywhere.

## OF3: `agreementAvailability: NOT_AVAILABLE` reflects the caller's Marketplace permissions, not the account's agreement (2026-11-06)

**What Roy established.** On the night of 2026-11-05, Roy made a real call that succeeded:
`us.anthropic.claude-haiku-4-5-20251001-v1:0` returned `{"text":"OK"}` (9 input and 4 output tokens). The blocker
was the IAM user's missing `aws-marketplace:ViewSubscriptions` and `aws-marketplace:Subscribe`, not an unaccepted
agreement. The `agreementAvailability` status reads NOT_AVAILABLE when **the caller** cannot complete the Marketplace
subscription, not when the account has not accepted the agreement.

**Evidence that fits.**
- The Cohere error text from OF1 (#5-#7) names exactly these two actions.
- A successful call can coexist with a NOT_AVAILABLE status, which was the contradiction in OF1. On 2026-11-06 at
  17:14Z, after the working Haiku 4.5 call, Sonnet 5.5 and Haiku 5.5 still read NOT_AVAILABLE
  (logs/availability.jsonl). The status field therefore cannot be used as an access gate for this IAM user.

**Still open: access is per model.** At 17:14Z on 2026-11-06, the first Tier A generation call to
`us.anthropic.claude-sonnet-5-5` was denied: "anthropic.claude-sonnet-5-5 is not available for this account". Zero
tokens were billed, and the script stopped by design. A working Haiku 4.5 call does not establish access to Sonnet
5.5 or Haiku 5.5. **Corrected the same day:** this is not a per-model subscription gap. The error ("not available
for this account ... contact AWS Sales") is account eligibility. A 1-token probe of every listed Anthropic profile
(logs/model_probe.jsonl, 2026-11-06) found 5 models callable: Haiku 4.5, Sonnet 4.5, Sonnet 4.6, Opus 4.5 and
Opus 4.6. Eligibility denials covered Sonnet 5 / 5.5, Haiku 5.5, Opus 4.7 / 4.8 / 5 / 5.5 and Fable 5 / 5.1. Opus 4.1
was denied as Legacy (not used in the last 30 days), and the Claude 3 and 3.5 models are end-of-life. Every one of
these models is listed by list-foundation-models as ACTIVE or LEGACY, so being listed does not mean a model is
callable either.

**Not explained.** Why Cohere v4 worked at OF1 #4 and then failed at #5-#6 within minutes.

**Cost.** About four hours of a 2-3 day study were spent polling an agreement status that could not change for
this caller. Earlier, a whole experimental axis (Cohere) was cut.

**Lesson.** On Bedrock, for third-party models, check access with the IAM action set and a minimal real call per
model ID. Do not rely on `get-foundation-model-availability` alone: its agreement field describes what this caller
can subscribe to.
