"""CLI entry point: download GSM8K and print a summary of the raw data.

Usage:
    python -m scripts.download_data
"""

from collections import Counter

from src.tasks.gsm8k import download_gsm8k, load_all


def main() -> None:
    download_gsm8k()
    problems = load_all()
    print(f"Total problems: {len(problems)}")

    counts = Counter(p["n_steps"] for p in problems)
    print(
        "n_steps histogram (calculator annotations per reference solution; each # ≈ 5 problems):"
    )
    for steps in sorted(counts):
        bar = "#" * max(1, counts[steps] // 5)
        print(f"  {steps:>2} steps: {counts[steps]:>4}  {bar}")


if __name__ == "__main__":
    main()
