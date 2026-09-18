"""Brier score: mean squared error between reported confidence and outcome.

More sensitive to individual large misses than ECE — e.g. one 99%-confident
wrong answer moves the Brier score a lot; ECE only sees it through its bin
average.
"""

import numpy as np


def brier_score(confidences, correctness) -> float:
    conf = np.asarray(confidences, dtype=float)
    correct = np.asarray(correctness, dtype=float)
    if len(conf) == 0:
        raise ValueError("brier_score() requires at least one prediction.")
    if conf.max() > 1.0:
        conf = conf / 100.0
    return float(np.mean((conf - correct) ** 2))
