"""Paired design power: n=13 pairs (same gold section, same fact). Pre-registration; no data.

Assumed model on latent log-rank (an ASSUMPTION, varied for sensitivity):
  log(rank_ij) = mu + u_i + delta * [j == worse condition] + e_ij
  u_i ~ N(0, tau^2)  shared by both questions of pair i (fact/section difficulty)
  e_ij ~ N(0, s^2)   question-specific
  sigma^2 = tau^2 + s^2 (total spread, as in power_rank.py); rho = tau^2 / sigma^2 = within-pair correlation
  rank = clip(ceil(exp(.)), 1, N_CHUNKS); mu chosen so that better-condition recall@5 = pA.
Tests (two-sided, alpha 0.05):
  mcnemar_r5   : exact McNemar on recall@5 (binomial test on discordant pairs)
  wilcoxon_full: Wilcoxon signed-rank on the uncensored rank among all chunks (zero differences dropped)
MDE = smallest delta at 80% power, reported as the TRUE recall@5 gap and TRUE MRR@5 gap.

  .venv/bin/python scripts/power_paired.py
"""
import numpy as np
from scipy.stats import binomtest, norm, wilcoxon

N_PAIRS, K, N_CHUNKS, ALPHA, REPS = 13, 5, 100, 0.05, 2000
rng = np.random.default_rng(0)


def to_rank(x):
    return np.clip(np.ceil(np.exp(x)), 1, N_CHUNKS).astype(int)


def rr(r):
    return np.where(r <= K, 1.0 / r, 0.0)


def mu_for(pa, sigma):
    return np.log(K) - sigma * norm.ppf(pa)


def true_gap(mu, sigma, delta, n=400_000):
    a = to_rank(rng.normal(mu, sigma, n)); b = to_rank(rng.normal(mu + delta, sigma, n))
    return float(np.mean(a <= K) - np.mean(b <= K)), float(rr(a).mean() - rr(b).mean())


def mcnemar_p(ha, hb):
    n10, n01 = int(np.sum(ha & ~hb)), int(np.sum(~ha & hb))
    return 1.0 if n10 + n01 == 0 else binomtest(n10, n10 + n01, 0.5).pvalue


def wilcoxon_p(a, b):
    d = a - b
    if np.all(d == 0):
        return 1.0
    return wilcoxon(a, b, zero_method="wilcox", alternative="two-sided").pvalue


def powers(pa, sigma, rho, delta):
    mu, tau, s = mu_for(pa, sigma), sigma * np.sqrt(rho), sigma * np.sqrt(1 - rho)
    hit = {"mcnemar_r5": 0, "wilcoxon_full": 0}
    for _ in range(REPS):
        u = rng.normal(0, tau, N_PAIRS)
        a = to_rank(mu + u + rng.normal(0, s, N_PAIRS))
        b = to_rank(mu + u + delta + rng.normal(0, s, N_PAIRS))
        hit["mcnemar_r5"] += mcnemar_p(a <= K, b <= K) < ALPHA
        hit["wilcoxon_full"] += wilcoxon_p(a, b) < ALPHA
    return {k: v / REPS for k, v in hit.items()}


def main():
    deltas = np.round(np.arange(0.125, 4.01, 0.125), 3)
    print(f"n = {N_PAIRS} pairs. MDE @80% power as TRUE recall@5 gap (MRR@5 gap)")
    print(" sigma | rho | Tier pA | mcnemar_r5      | wilcoxon_full")
    for sigma in (1.0, 1.5):
        for rho in (0.3, 0.6):
            for pa in (0.6, 0.7, 0.8, 0.9):
                mu, found = mu_for(pa, sigma), {}
                for d in deltas:
                    for t, v in powers(pa, sigma, rho, d).items():
                        if t not in found and v >= 0.80:
                            found[t] = true_gap(mu, sigma, d)
                    if len(found) == 2:
                        break
                cells = [f"{100*found[t][0]:3.0f} pts ({found[t][1]:.2f})" if t in found else "not reached"
                         for t in ("mcnemar_r5", "wilcoxon_full")]
                print(f"  {sigma:.1f}  | {rho:.1f} |   {pa:.1f}   | {cells[0]:15s} | {cells[1]}")


if __name__ == "__main__":
    main()
