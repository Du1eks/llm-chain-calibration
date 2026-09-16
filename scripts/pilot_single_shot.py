"""Pilot: run single-shot on 3 GSM8K problems, print answer/confidence/cost.

Usage:
    python -m scripts.pilot_single_shot
"""

from src.agents.single_shot import solve
from src.tasks.gsm8k import load_subset
from src.tasks.grading import extract_reference_answer, is_correct
from src.utils.llm import CostTracker


def main() -> None:
    problems = load_subset(n=3, seed=42)
    tracker = CostTracker(max_spend_usd=0.10)

    for problem in problems:
        reference = extract_reference_answer(problem["answer"])
        result = solve(problem["question"], tracker=tracker)
        correct = is_correct(result.answer, reference)

        print(f"--- {problem['id']} (n_steps={problem['n_steps']}) ---")
        print(f"Question: {problem['question'][:100]}...")
        print(
            f"Reference: {reference}  |  Model answer: {result.answer}  |  Correct: {correct}"
        )
        print(f"Confidence: {result.confidence}")
        print()

    print(f"Total: {tracker.summary()}")
    print(f"Estimated cost for 100 problems: ${tracker.cost_usd / 3 * 100:.4f}")


if __name__ == "__main__":
    main()
