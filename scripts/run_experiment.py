"""Run the full experiment: single-shot and chain conditions on the same
GSM8K sample, writing results incrementally with resume support.

Usage:
    python -m scripts.run_experiment --limit 5      # smoke test
    python -m scripts.run_experiment                # full run (config.SAMPLE_SIZE)
    python -m scripts.run_experiment --condition single_shot
"""

import argparse
import json

from config import config
from src.agents.chain import solve as chain_solve
from src.agents.single_shot import solve as single_shot_solve
from src.tasks.gsm8k import load_subset
from src.tasks.grading import extract_reference_answer, is_correct
from src.utils.llm import CostTracker

RESULT_FILES = {
    "single_shot": config.DATA_RESULTS / "single_shot.jsonl",
    "chain": config.DATA_RESULTS / "chain.jsonl",
}


def _load_done_ids(path) -> set[str]:
    """IDs already written to path — resume skips these."""
    if not path.exists():
        return set()
    done = set()
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                done.add(json.loads(line)["id"])
    return done


def _append_result(path, record: dict) -> None:
    config.DATA_RESULTS.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def run_single_shot(problems: list[dict], tracker: CostTracker) -> None:
    path = RESULT_FILES["single_shot"]
    done = _load_done_ids(path)
    remaining = [p for p in problems if p["id"] not in done]
    print(f"single_shot: {len(done)} already done, {len(remaining)} remaining")

    for problem in remaining:
        tokens_before = tracker.input_tokens + tracker.output_tokens
        reference = extract_reference_answer(problem["answer"])
        result = single_shot_solve(problem["question"], tracker=tracker)
        correct = is_correct(result.answer, reference)
        tokens_used = (tracker.input_tokens + tracker.output_tokens) - tokens_before

        _append_result(
            path,
            {
                "id": problem["id"],
                "reference": reference,
                "answer": result.answer,
                "confidence": result.confidence,
                "correct": correct,
                "tokens_used": tokens_used,
            },
        )
        print(
            f"[single_shot] {problem['id']}: correct={correct} "
            f"confidence={result.confidence} (total spend ${tracker.cost_usd:.4f})"
        )


def run_chain(problems: list[dict], tracker: CostTracker) -> None:
    path = RESULT_FILES["chain"]
    done = _load_done_ids(path)
    remaining = [p for p in problems if p["id"] not in done]
    print(f"chain: {len(done)} already done, {len(remaining)} remaining")

    for problem in remaining:
        tokens_before = tracker.input_tokens + tracker.output_tokens
        reference = extract_reference_answer(problem["answer"])
        result = chain_solve(problem["question"], tracker=tracker)
        correct = is_correct(result.final_answer, reference)
        tokens_used = (tracker.input_tokens + tracker.output_tokens) - tokens_before

        _append_result(
            path,
            {
                "id": problem["id"],
                "reference": reference,
                "plan_confidence": result.plan_confidence,
                "executor_answer": result.executor_answer,
                "executor_confidence": result.executor_confidence,
                "final_answer": result.final_answer,
                "final_confidence": result.final_confidence,
                "correct": correct,
                "tokens_used": tokens_used,
            },
        )
        print(
            f"[chain] {problem['id']}: correct={correct} "
            f"final_confidence={result.final_confidence} (total spend ${tracker.cost_usd:.4f})"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=config.SAMPLE_SIZE)
    parser.add_argument(
        "--condition", choices=["single_shot", "chain", "both"], default="both"
    )
    args = parser.parse_args()

    problems = load_subset(
        n=args.limit, seed=config.RANDOM_SEED, min_steps=config.MIN_STEPS
    )
    tracker = CostTracker()  # enforces config.MAX_SPEND_USD across the whole run

    if args.condition in ("single_shot", "both"):
        run_single_shot(problems, tracker)
    if args.condition in ("chain", "both"):
        run_chain(problems, tracker)

    print()
    print(f"Done. {tracker.summary()}")


if __name__ == "__main__":
    main()
