"""Reliability diagram: reported confidence vs. actual accuracy, per bin,
for both conditions on the same axes.
"""

import matplotlib.pyplot as plt

from src.eval.ece import reliability_bins


def plot_reliability(
    confidences_a,
    correctness_a,
    label_a,
    confidences_b,
    correctness_b,
    label_b,
    n_bins: int = 10,
    output_path=None,
):
    """Draw the reliability diagram for two conditions and save it.

    Marker size is proportional to how many predictions fall in that bin —
    a bin with 2 points should look less trustworthy than one with 40.
    """
    fig, ax = plt.subplots(figsize=(6, 6))

    ax.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        color="gray",
        linewidth=1,
        label="Perfect calibration",
    )

    for confidences, correctness, label, color in [
        (confidences_a, correctness_a, label_a, "tab:blue"),
        (confidences_b, correctness_b, label_b, "tab:orange"),
    ]:
        bins = reliability_bins(confidences, correctness, n_bins=n_bins)
        if not bins:
            continue
        x = [b["mean_confidence"] for b in bins]
        y = [b["accuracy"] for b in bins]
        sizes = [20 + b["count"] * 4 for b in bins]
        ax.scatter(x, y, s=sizes, color=color, alpha=0.7, label=label, zorder=3)
        ax.plot(x, y, color=color, alpha=0.4, linewidth=1, zorder=2)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Reported confidence")
    ax.set_ylabel("Actual accuracy")
    ax.set_title("Reliability diagram: single-shot vs. chain")
    ax.legend(loc="upper left")
    ax.set_aspect("equal")

    fig.tight_layout()
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150)
        print(f"Saved: {output_path}")
    return fig
