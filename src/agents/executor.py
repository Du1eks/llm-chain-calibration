"""Chain step 2: carry out the planner's plan, produce an answer.

Deliberately does not see the planner's confidence — only its plan text —
so this stage's confidence reflects its own execution, not an inherited
number from the previous stage.
"""

from src.agents.schemas import ExecutorOutput
from src.utils.llm import CostTracker, call_structured

SYSTEM_PROMPT = """\
You are the execution stage of a problem-solving pipeline. You will see a \
grade-school math word problem and a plan for solving it, written by a \
previous stage. Carry out the plan step by step and report the final \
numeric answer.

Report your confidence (0-100) that your answer is correct. Use the full \
range honestly — do not default to a fixed number for every problem. If \
the plan was unclear or you had to guess at any step, reflect that with \
a lower number.
"""


def execute(
    question: str, plan_text: str, tracker: CostTracker | None = None
) -> ExecutorOutput:
    user = f"Problem:\n{question}\n\nPlan:\n{plan_text}"
    parsed, _usage = call_structured(
        system=SYSTEM_PROMPT,
        user=user,
        output_format=ExecutorOutput,
        tracker=tracker,
    )
    return parsed
