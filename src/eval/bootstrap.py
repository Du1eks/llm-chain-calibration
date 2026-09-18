"""Bootstrap confidence interval for the difference in ECE between two
conditions (e.g. single-shot vs. chain) — is the observed gap real or noise?
"""

import numpy as np

from src.eval.ece import ece


def bootstrap_ece_diff(
    confidences_a,
    correctness_a,
    confidences_b,
    correctness_b,
    n_bins: int = 10,
    n_resamples: int = 2000,
    seed: int = 0,
) -> dict:
    """Bootstrap CI for ece(a) - ece(b).

    Resamples each condition independently (with replacement, same size
    as the original), recomputes ECE each time, and reports the observed
    difference plus a 95% percentile CI over the resampled differences.
    """
    conf_a = np.asarray(confidences_a, dtype=float)
    correct_a = np.asarray(correctness_a, dtype=float)
    conf_b = np.asarray(confidences_b, dtype=float)
    correct_b = np.asarray(correctness_b, dtype=float)

    observed = ece(conf_a, correct_a, n_bins) - ece(conf_b, correct_b, n_bins)

    rng = np.random.default_rng(seed)
    diffs = np.empty(n_resamples)
    for i in range(n_resamples):
        idx_a = rng.integers(0, len(conf_a), len(conf_a))
        idx_b = rng.integers(0, len(conf_b), len(conf_b))
        diffs[i] = ece(conf_a[idx_a], correct_a[idx_a], n_bins) - ece(
            conf_b[idx_b], correct_b[idx_b], n_bins
        )

    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return {
        "observed_diff": float(observed),
        "ci_low": float(lo),
        "ci_high": float(hi),
        "significant": bool(lo > 0 or hi < 0),  # CI excludes 0
    }
