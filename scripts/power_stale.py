"""Stale-fact mitigation power, pre-registration (no data). Exact enumeration, no simulation.

Design: n facts, each measured WITHOUT (baseline) and WITH a mitigation, in one model arm. Outcome per answer:
propagated (1) or not (0), using the headline bucket from reports/stale_fact_rule.md.
Two-sided, alpha 0.05, 80% power. The MDE is reported as the smallest drop p0 -> p1 in propagation rate.

Tests:
  wilson_overlap : the ORIGINAL rule (two independent Wilson 95% CIs must not overlap). Shown for comparison only.
  fisher         : unpaired Fisher exact, n vs n (what an independent-groups analysis would use).
  mcnemar_exact  : paired, exact binomial test on discordant facts.

Paired model: a fact propagated at baseline stays propagated with probability s. A fact NOT propagated at baseline
becomes propagated under the mitigation with probability b (the mitigation "breaks" it). Then
p1 = p0*s + (1-p0)*b, fixed = p0*(1-s), broken = (1-p0)*b. b = 0 is the most favourable case for McNemar
(the mitigation never hurts). b = 0.1 is shown as a sensitivity case.

  .venv/bin/python scripts/power_stale.py
"""
from functools import lru_cache
from math import comb, sqrt

from scipy.stats import binomtest, fisher_exact

ALPHA, POWER = 0.05, 0.80


def wilson(x, n, z=1.959964):
    p = x / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


@lru_cache(None)
def fisher_rej(x0, x1, n):
    return fisher_exact([[x0, n - x0], [x1, n - x1]])[1] < ALPHA


@lru_cache(None)
def wilson_rej(x0, x1, n):
    (l0, h0), (l1, h1) = wilson(x0, n), wilson(x1, n)
    return h1 < l0 or h0 < l1


@lru_cache(None)
def mcn_rej(f, k):
    return f + k > 0 and binomtest(f, f + k, 0.5).pvalue < ALPHA


def binpmf(x, n, p):
    return comb(n, x) * p ** x * (1 - p) ** (n - x)


def power_unpaired(p0, p1, n, rej):
    return sum(binpmf(a, n, p0) * binpmf(b, n, p1) for a in range(n + 1) for b in range(n + 1) if rej(a, b, n))


def power_paired(p0, p1, n, b):
    s = (p1 - (1 - p0) * b) / p0
    if not 0 <= s <= 1:
        return None
    pf, pb = p0 * (1 - s), (1 - p0) * b
    tot = 0.0
    for f in range(n + 1):
        for k in range(n + 1 - f):
            if mcn_rej(f, k):
                tot += comb(n, f) * comb(n - f, k) * pf ** f * pb ** k * (1 - pf - pb) ** (n - f - k)
    return tot


def mde(p0, fn):
    """Smallest drop d (step 0.01) whose power is >= POWER; None if even p1 = 0 does not reach it."""
    for i in range(1, int(round(p0 * 100)) + 1):
        p1 = round(p0 - i / 100, 4)
        pw = fn(p0, p1)
        if pw is not None and pw >= POWER:
            return round(p0 - p1, 2), round(pw, 3)
    return None


def main():
    for n in (11, 22, 33):
        tag = "the design: 11 facts" if n == 11 else "if facts x phrasings were independent (OPTIMISTIC, see note)"
        print(f"\n=== n = {n} per cell ({tag})")
        print(" baseline p0 | wilson_overlap | fisher (unpaired) | mcnemar b=0 | mcnemar b=0.1")
        for p0 in (0.3, 0.5, 0.7, 0.9):
            cells = [
                mde(p0, lambda a, c: power_unpaired(a, c, n, wilson_rej)),
                mde(p0, lambda a, c: power_unpaired(a, c, n, fisher_rej)),
                mde(p0, lambda a, c: power_paired(a, c, n, 0.0)),
                mde(p0, lambda a, c: power_paired(a, c, n, 0.1)),
            ]
            out = [f"-{100 * m[0]:.0f} pts" if m else "not reached" for m in cells]
            print(f"    {p0:.1f}      | {out[0]:14s} | {out[1]:17s} | {out[2]:11s} | {out[3]}")
    print("\nMcNemar floor at n=11: the smallest rejecting outcome is 6 fixed / 0 broken (p = 0.031); "
          "5/0 gives p = 0.0625.")


if __name__ == "__main__":
    main()
