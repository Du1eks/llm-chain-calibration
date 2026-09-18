"""Tests for src/eval/{ece,brier,bootstrap}.py — synthetic data, zero API calls."""

import numpy as np
import pytest

from src.eval.bootstrap import bootstrap_ece_diff
from src.eval.brier import brier_score
from src.eval.ece import ece, reliability_bins


def test_ece_perfect_calibration():
    # 10 confidence levels, each with exactly that fraction correct.
    confidences = []
    correctness = []
    rng = np.random.default_rng(0)
    for level in range(0, 100, 10):
        c = level / 100
        n = 100
        confidences.extend([level] * n)
        correctness.extend(rng.random(n) < c)
    assert ece(confidences, correctness, n_bins=10) < 0.05


def test_ece_always_confident_half_right():
    confidences = [100] * 200
    rng = np.random.default_rng(1)
    correctness = (rng.random(200) < 0.5).astype(int)
    result = ece(confidences, correctness, n_bins=10)
    assert abs(result - 0.5) < 0.05


def test_ece_accepts_0_1_scale():
    confidences_pct = [90, 90, 10, 10]
    confidences_frac = [0.9, 0.9, 0.1, 0.1]
    correctness = [1, 0, 0, 1]
    assert (
        abs(ece(confidences_pct, correctness) - ece(confidences_frac, correctness))
        < 1e-9
    )


def test_ece_empty_raises():
    with pytest.raises(ValueError):
        ece([], [])


def test_reliability_bins_shape():
    confidences = [10, 20, 90, 95]
    correctness = [0, 1, 1, 1]
    bins = reliability_bins(confidences, correctness, n_bins=10)
    assert all(0 <= b["bin_lo"] < b["bin_hi"] <= 1 for b in bins)
    assert sum(b["count"] for b in bins) == 4


def test_brier_perfect_predictions():
    assert brier_score([100, 0], [1, 0]) == 0.0


def test_brier_worst_predictions():
    assert brier_score([100, 0], [0, 1]) == 1.0


def test_brier_matches_manual_calc():
    # confidence 70%, correct -> (0.7-1)^2 = 0.09
    # confidence 70%, wrong -> (0.7-0)^2 = 0.49
    # mean = 0.29
    result = brier_score([70, 70], [1, 0])
    assert abs(result - 0.29) < 1e-9


def test_bootstrap_ece_diff_same_data_no_difference():
    rng = np.random.default_rng(2)
    conf = list(rng.integers(50, 100, 100))
    correct = list((rng.random(100) < 0.8).astype(int))
    result = bootstrap_ece_diff(conf, correct, conf, correct, n_resamples=200)
    assert abs(result["observed_diff"]) < 1e-9
    assert not result["significant"]
