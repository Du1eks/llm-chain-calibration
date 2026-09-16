"""Grading: extract GSM8K reference answers, check model answers against them."""

import re


def extract_reference_answer(raw_answer: str) -> str:
    """Pull the final numeric answer out of a GSM8K reference solution.

    GSM8K reference answers end with a line like "#### 72". Returns the
    raw string after "####", stripped — normalization happens in
    is_correct(), not here, so callers can still inspect the raw string.
    """
    match = re.search(r"####\s*(.+)", raw_answer)
    if not match:
        raise ValueError(f"No '#### <answer>' found in reference: {raw_answer!r}")
    return match.group(1).strip()


def _normalize_number(value: str) -> float:
    """Turn a loosely-formatted numeric string into a float.

    Handles leading/trailing whitespace, "$" signs, "%" signs, and
    thousands separators ("1,234"). Anything else that still doesn't
    parse as a float is a genuine failure and should raise.
    """
    cleaned = value.strip().replace(",", "").replace("$", "").rstrip("%").strip()
    return float(cleaned)


def is_correct(predicted: str, reference: str, tolerance: float = 1e-4) -> bool:
    """Compare a model's predicted answer to the GSM8K reference answer.

    Both are normalized to floats and compared with a small tolerance
    (handles "18" vs "18.0"). Returns False, not an exception, if the
    predicted answer can't be parsed as a number — an unparsable answer
    is simply wrong, not a crash.
    """
    try:
        predicted_value = _normalize_number(str(predicted))
    except (ValueError, TypeError):
        return False
    reference_value = _normalize_number(str(reference))
    return abs(predicted_value - reference_value) <= tolerance
