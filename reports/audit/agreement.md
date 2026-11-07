# Hand-audit agreement (scripts/score_audit.py)

## Worksheet 1 (census of MIXED/OLD_FLAGGED/OTHER): n = 36, agreement 0.14, Cohen's kappa -0.01

| rule class \ Roy | propagated | current | neither |
|---|---|---|---|
| MIXED (propagated) | 5 | 20 | 8 |
| OTHER (neither) | 0 | 3 | 0 |

## Worksheet 2 (random rest): n = 18, agreement 0.83, Cohen's kappa 0.00

| rule class \ Roy | propagated | current | neither |
|---|---|---|---|
| CURRENT (current) | 0 | 13 | 0 |
| CURRENT_FLAGGED (current) | 0 | 2 | 0 |
| PROPAGATED (propagated) | 0 | 3 | 0 |

## Combined, unweighted: n = 54, agreement 0.37, Cohen's kappa 0.12

| rule class \ Roy | propagated | current | neither |
|---|---|---|---|
| CURRENT (current) | 0 | 13 | 0 |
| CURRENT_FLAGGED (current) | 0 | 2 | 0 |
| MIXED (propagated) | 5 | 20 | 8 |
| PROPAGATED (propagated) | 0 | 3 | 0 |
| OTHER (neither) | 0 | 3 | 0 |

**Population estimate of headline-bucket agreement over all 132 fact answers (strata weighted 36 / 96): 0.64.** Pre-registered threshold 0.85: NOT met; the stale-fact results are labelled rule-dependent, with Roy's rates beside them.

## X1 (scored separately): agreement 4/4; rule CORRECT / Roy CORRECT, rule CORRECT / Roy CORRECT, rule CORRECT / Roy CORRECT, rule CORRECT / Roy CORRECT

