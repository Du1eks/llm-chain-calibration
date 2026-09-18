"""Chain step 3: check the plan + answer, report a final verdict.

Deliberately does not see the planner's or executor's confidence — only
their text output — so a high final confidence has to come from the
verifier's own assessment, not from copying an earlier number.
"""

from src.agents.schemas import VerifierOutput
from src.utils.llm import CostTracker, call_structured

SYSTEM_PROMPT = """\
You are the verification stage of a problem-solving pipeline. You will \
see a grade-school math word problem, a plan for solving it, and an \
answer produced by carrying out that plan. Check whether the answer is \
correct by re-deriving it (or checking the arithmetic) — do not simply \
trust the plan and answer because they look complete and well-formatted.

Report a brief verdict, your final answer (the given answer if correct, \
a corrected one if you find an error), and your confidence (0-100) that \
your final answer is correct. Use the full range honestly.
"""


def verify(
    question: str, plan_text: str, answer: str, tracker: CostTracker | None = None
) -> VerifierOutput:
    user = f"Problem:\n{question}\n\nPlan:\n{plan_text}\n\nProposed answer: {answer}"
    parsed, _usage = call_structured(
        system=SYSTEM_PROMPT,
        user=user,
        output_format=VerifierOutput,
        tracker=tracker,
    )
    return parsed
