"""Pilot: run the chain (Planner -> Executor -> Verifier) on the same 3
GSM8K problems as scripts/pilot_single_shot.py, for a cost/behavior
comparison between conditions.

Usage:
    python -m scripts.pilot_chain
"""

from src.agents.chain import solve
from src.tasks.gsm8k import load_subset
from src.tasks.grading import extract_reference_answer, is_correct
from src.utils.llm import CostTracker


def main() -> None:
    problems = load_subset(n=3, seed=42)
    tracker = CostTracker(max_spend_usd=0.20)

    for problem in problems:
        reference = extract_reference_answer(problem["answer"])
        result = solve(problem["question"], tracker=tracker)
        correct = is_correct(result.final_answer, reference)

        print(f"--- {problem['id']} (n_steps={problem['n_steps']}) ---")
        print(f"Question: {problem['question'][:100]}...")
        print(
            f"Reference: {reference}  |  Final answer: {result.final_answer}  |  Correct: {correct}"
        )
        print(
            f"Confidences — planner: {result.plan_confidence}, "
            f"executor: {result.executor_confidence}, "
            f"verifier (final): {result.final_confidence}"
        )
        print()

    print(f"Total: {tracker.summary()}")
    print(f"Estimated cost for 100 problems: ${tracker.cost_usd / 3 * 100:.4f}")


if __name__ == "__main__":
    main()
