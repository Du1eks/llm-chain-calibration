"""Condition B: Planner -> Executor -> Verifier chain.

Each stage only sees the previous stage's text output, never its
confidence — this is what the calibration hypothesis in the project
plan actually tests (see docs/plan_projekta.md).
"""

from dataclasses import dataclass

from src.agents.executor import execute
from src.agents.planner import plan
from src.agents.verifier import verify
from src.utils.llm import CostTracker


@dataclass
class ChainResult:
    plan_text: str
    plan_confidence: int
    executor_answer: str
    executor_confidence: int
    verifier_verdict: str
    final_answer: str
    final_confidence: int


def solve(question: str, tracker: CostTracker | None = None) -> ChainResult:
    """Run the full three-stage chain on one GSM8K question."""
    planner_out = plan(question, tracker=tracker)
    executor_out = execute(question, planner_out.plan, tracker=tracker)
    verifier_out = verify(
        question, planner_out.plan, executor_out.answer, tracker=tracker
    )

    return ChainResult(
        plan_text=planner_out.plan,
        plan_confidence=planner_out.confidence,
        executor_answer=executor_out.answer,
        executor_confidence=executor_out.confidence,
        verifier_verdict=verifier_out.verdict,
        final_answer=verifier_out.final_answer,
        final_confidence=verifier_out.confidence,
    )
