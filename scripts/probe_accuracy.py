"""Accuracy probe (plan step 7): measure single-shot accuracy on N problems
to decide whether the random 100-problem sample will have enough errors to
measure calibration, before committing to the full run.

Usage:
    python -m scripts.probe_accuracy [--min-steps N]
"""

import argparse

from src.agents.single_shot import solve
from src.tasks.gsm8k import load_subset
from src.tasks.grading import extract_reference_answer, is_correct
from src.utils.llm import CostTracker

PROBE_N = 20
ACCURACY_THRESHOLD = 0.95


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--min-steps",
        type=int,
        default=0,
        help="Filter to problems with at least this many calculator steps (harder subset).",
    )
    args = parser.parse_args()

    # seed=123, deliberately different from the pilot (seed=42) and from
    # the final experiment sample (also seed=42) — the probe should not
    # overlap with problems used elsewhere.
    problems = load_subset(n=PROBE_N, seed=123, min_steps=args.min_steps)
    tracker = CostTracker(max_spend_usd=0.20)

    n_correct = 0
    for problem in problems:
        reference = extract_reference_answer(problem["answer"])
        result = solve(problem["question"], tracker=tracker)
        correct = is_correct(result.answer, reference)
        n_correct += correct
        status = "OK " if correct else "ERR"
        print(
            f"[{status}] {problem['id']} (n_steps={problem['n_steps']}) conf={result.confidence:>3}"
        )

    accuracy = n_correct / len(problems)
    print()
    print(
        f"Accuracy: {n_correct}/{len(problems)} = {accuracy:.1%}  (min_steps={args.min_steps})"
    )
    print(tracker.summary())

    if accuracy > ACCURACY_THRESHOLD:
        print(
            f"\nAccuracy > {ACCURACY_THRESHOLD:.0%} — GSM8K may be too easy for this model. "
            "Re-run with a higher --min-steps to probe the harder subset, e.g.:\n"
            "  python -m scripts.probe_accuracy --min-steps 5"
        )
    else:
        print(
            f"\nAccuracy <= {ACCURACY_THRESHOLD:.0%} — plenty of errors expected. "
            f"Proceed with the full 100-problem sample using min_steps={args.min_steps}."
        )


if __name__ == "__main__":
    main()
