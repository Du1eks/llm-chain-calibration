"""GSM8K loading: download the test split, sample a fixed subset."""

import json
import random
import re

import requests

from config import config


def download_gsm8k(force: bool = False) -> None:
    """Download the GSM8K test split into data/raw/, unless already present."""
    if config.GSM8K_RAW_FILE.exists() and not force:
        print(f"Already downloaded: {config.GSM8K_RAW_FILE}")
        return

    config.DATA_RAW.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {config.GSM8K_URL} ...")
    response = requests.get(config.GSM8K_URL, timeout=30)
    response.raise_for_status()
    config.GSM8K_RAW_FILE.write_text(response.text, encoding="utf-8")
    print(f"Saved to {config.GSM8K_RAW_FILE}")


def load_all() -> list[dict]:
    """Read every GSM8K problem from the raw file, in file order.

    Each item: {id, question, answer, n_steps}. `answer` is the full
    reference solution (reasoning + "#### <number>"), not just the final
    number — see src/tasks/grading.py (step 3) for extracting that number.
    `n_steps` counts "<<...>>" calculator annotations, used as a rough
    difficulty proxy.
    """
    if not config.GSM8K_RAW_FILE.exists():
        raise FileNotFoundError(
            f"{config.GSM8K_RAW_FILE} not found — run download_gsm8k() first."
        )
    problems = []
    with config.GSM8K_RAW_FILE.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            problems.append(
                {
                    "id": f"gsm8k-{i}",
                    "question": record["question"],
                    "answer": record["answer"],
                    "n_steps": len(re.findall(r"<<[^>]*>>", record["answer"])),
                }
            )
    return problems


def load_subset(
    n: int = config.SAMPLE_SIZE,
    seed: int = config.RANDOM_SEED,
    min_steps: int = 0,
) -> list[dict]:
    """Return a reproducible random subset of n problems.

    min_steps filters to harder problems before sampling — used only if
    the accuracy probe (plan step 7) shows GSM8K is too easy at
    min_steps=0 for the chosen model.
    """
    problems = load_all()
    if min_steps > 0:
        problems = [p for p in problems if p["n_steps"] >= min_steps]
    if n > len(problems):
        raise ValueError(
            f"Requested {n} problems but only {len(problems)} available "
            f"(min_steps={min_steps})."
        )
    rng = random.Random(seed)
    return rng.sample(problems, n)
