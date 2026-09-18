"""Step 12: compute ECE, Brier, and the reliability diagram from the full
experiment's results (data/results/{single_shot,chain}.jsonl).

Usage:
    python -m scripts.analyze_results
"""

import json

from config import config
from src.eval.bootstrap import bootstrap_ece_diff
from src.eval.brier import brier_score
from src.eval.ece import ece
from src.eval.reliability_plot import plot_reliability


def _load_jsonl(path):
    records = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def main() -> None:
    single_shot = _load_jsonl(config.DATA_RESULTS / "single_shot.jsonl")
    chain = _load_jsonl(config.DATA_RESULTS / "chain.jsonl")

    conf_a = [r["confidence"] for r in single_shot]
    correct_a = [r["correct"] for r in single_shot]
    conf_b = [r["final_confidence"] for r in chain]
    correct_b = [r["correct"] for r in chain]

    accuracy_a = sum(correct_a) / len(correct_a)
    accuracy_b = sum(correct_b) / len(correct_b)
    print(f"single_shot: n={len(single_shot)}, accuracy={accuracy_a:.1%}")
    print(f"chain:       n={len(chain)}, accuracy={accuracy_b:.1%}")
    print()

    ece_a = ece(conf_a, correct_a)
    ece_b = ece(conf_b, correct_b)
    brier_a = brier_score(conf_a, correct_a)
    brier_b = brier_score(conf_b, correct_b)

    print(f"ECE    single_shot={ece_a:.4f}   chain={ece_b:.4f}")
    print(f"Brier  single_shot={brier_a:.4f}   chain={brier_b:.4f}")
    print()

    diff = bootstrap_ece_diff(conf_a, correct_a, conf_b, correct_b)
    print(
        f"Bootstrap 95% CI for ECE(single_shot) - ECE(chain): "
        f"{diff['observed_diff']:.4f}  [{diff['ci_low']:.4f}, {diff['ci_high']:.4f}]  "
        f"significant={diff['significant']}"
    )

    output_path = config.FIGURES / "reliability_diagram.png"
    plot_reliability(
        conf_a,
        correct_a,
        "single_shot",
        conf_b,
        correct_b,
        "chain",
        output_path=output_path,
    )

    summary = {
        "n": len(single_shot),
        "model": config.MODEL_ID,
        "min_steps": config.MIN_STEPS,
        "seed": config.RANDOM_SEED,
        "single_shot": {"accuracy": accuracy_a, "ece": ece_a, "brier": brier_a},
        "chain": {"accuracy": accuracy_b, "ece": ece_b, "brier": brier_b},
        "bootstrap_ece_diff": diff,
    }
    summary_path = config.FIGURES.parent / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved: {summary_path}")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
