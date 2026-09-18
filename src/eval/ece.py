"""Expected Calibration Error (ECE): bin predictions by reported confidence,
compare mean confidence to actual accuracy in each bin.
"""

import numpy as np


def _to_unit_interval(confidences: np.ndarray) -> np.ndarray:
    """Accept confidence as 0-100 or 0-1, always return 0-1."""
    return confidences / 100.0 if confidences.max() > 1.0 else confidences


def ece(confidences, correctness, n_bins: int = 10) -> float:
    """Expected Calibration Error: weighted average |confidence - accuracy|
    across n_bins equal-width bins over [0, 1]. Empty bins are skipped.
    """
    conf = _to_unit_interval(np.asarray(confidences, dtype=float))
    correct = np.asarray(correctness, dtype=float)
    if len(conf) == 0:
        raise ValueError("ece() requires at least one prediction.")

    bin_ids = np.minimum((conf * n_bins).astype(int), n_bins - 1)

    total = len(conf)
    error = 0.0
    for b in range(n_bins):
        mask = bin_ids == b
        if not mask.any():
            continue
        bin_confidence = conf[mask].mean()
        bin_accuracy = correct[mask].mean()
        weight = mask.sum() / total
        error += weight * abs(bin_confidence - bin_accuracy)
    return float(error)


def reliability_bins(confidences, correctness, n_bins: int = 10) -> list[dict]:
    """Per-bin breakdown, used by the reliability plot (step 11).

    Returns a list of {bin_lo, bin_hi, mean_confidence, accuracy, count}
    for each non-empty bin.
    """
    conf = _to_unit_interval(np.asarray(confidences, dtype=float))
    correct = np.asarray(correctness, dtype=float)
    bin_ids = np.minimum((conf * n_bins).astype(int), n_bins - 1)

    bins = []
    for b in range(n_bins):
        mask = bin_ids == b
        if not mask.any():
            continue
        bins.append(
            {
                "bin_lo": b / n_bins,
                "bin_hi": (b + 1) / n_bins,
                "mean_confidence": float(conf[mask].mean()),
                "accuracy": float(correct[mask].mean()),
                "count": int(mask.sum()),
            }
        )
    return bins
