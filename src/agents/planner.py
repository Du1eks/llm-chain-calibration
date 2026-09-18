"""Chain step 1: break a problem into a plan. Does not solve it."""

from src.agents.schemas import PlannerOutput
from src.utils.llm import CostTracker, call_structured

SYSTEM_PROMPT = """\
You are the planning stage of a problem-solving pipeline. You will see a \
grade-school math word problem. Do NOT solve it — break it down into a \
numbered list of the steps needed to solve it (what to calculate, in what \
order). Someone else will carry out your plan.

Report your confidence (0-100) that this plan is correct and sufficient \
to solve the problem — not confidence in a final numeric answer, since \
you are not computing one. Use the full range honestly.
"""


def plan(question: str, tracker: CostTracker | None = None) -> PlannerOutput:
    parsed, _usage = call_structured(
        system=SYSTEM_PROMPT,
        user=question,
        output_format=PlannerOutput,
        tracker=tracker,
    )
    return parsed
