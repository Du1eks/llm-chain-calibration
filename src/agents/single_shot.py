"""Condition A: single-shot solve + confidence report, one Claude call."""

from src.agents.schemas import SingleShotOutput
from src.utils.llm import CostTracker, call_structured

SYSTEM_PROMPT = """\
You solve grade-school math word problems. Work through the problem step \
by step, then report your final numeric answer and your confidence that \
it is correct.

Confidence is a number from 0 to 100: 0 means you are certain the answer \
is wrong or you could not solve it, 100 means you are certain it is right. \
Use the full range honestly — do not default to a fixed number like 90 \
for every problem. If the problem was easy and you are sure of each step, \
say so with a high number. If you had to guess at any step, reflect that \
with a lower number.
"""


def solve(question: str, tracker: CostTracker | None = None) -> SingleShotOutput:
    """Run the single-shot condition on one GSM8K question."""
    parsed, _usage = call_structured(
        system=SYSTEM_PROMPT,
        user=question,
        output_format=SingleShotOutput,
        tracker=tracker,
    )
    return parsed
