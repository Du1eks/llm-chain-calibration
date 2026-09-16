"""Tests for src/tasks/grading.py — zero API calls."""

import pytest

from src.tasks.grading import extract_reference_answer, is_correct


def test_extract_reference_answer_simple():
    raw = "Natalia sold 48 clips.\n#### 72"
    assert extract_reference_answer(raw) == "72"


def test_extract_reference_answer_with_comma_thousands():
    raw = "Total is a lot.\n#### 1,234"
    assert extract_reference_answer(raw) == "1,234"


def test_extract_reference_answer_missing_marker_raises():
    with pytest.raises(ValueError):
        extract_reference_answer("no marker here")


@pytest.mark.parametrize(
    "predicted,reference,expected",
    [
        ("72", "72", True),
        ("72.0", "72", True),
        ("72", "72.0", True),
        (" 72 ", "72", True),
        ("$72", "72", True),
        ("1,234", "1234", True),
        ("1234", "1,234", True),
        ("-5", "-5", True),
        ("-5", "5", False),
        ("71", "72", False),
        ("72.001", "72", False),  # outside default tolerance
        ("not a number", "72", False),
        ("", "72", False),
    ],
)
def test_is_correct(predicted, reference, expected):
    assert is_correct(predicted, reference) == expected


def test_is_correct_custom_tolerance():
    assert is_correct("72.05", "72", tolerance=0.1) is True
    assert is_correct("72.05", "72", tolerance=0.01) is False
