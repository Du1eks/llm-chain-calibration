"""Pydantic schemas for every agent's structured output.

Each agent reports a numeric answer plus a confidence 0-100. Field
descriptions double as prompt guidance — Claude sees them as part of
the JSON schema it must satisfy.
"""

from pydantic import BaseModel, Field


class SingleShotOutput(BaseModel):
    """Condition A: one call solves the problem and reports confidence."""

    reasoning: str = Field(description="Brief step-by-step reasoning.")
    answer: str = Field(description="The final numeric answer, digits only.")
    confidence: int = Field(
        ge=0, le=100, description="Confidence 0-100 that the answer is correct."
    )


class PlannerOutput(BaseModel):
    """Chain step 1: break the problem into steps. Does not solve it."""

    plan: str = Field(description="Numbered list of steps needed to solve the problem.")
    confidence: int = Field(
        ge=0,
        le=100,
        description="Confidence 0-100 that this plan is correct and sufficient.",
    )


class ExecutorOutput(BaseModel):
    """Chain step 2: carry out the plan, produce an answer."""

    reasoning: str = Field(description="Step-by-step execution of the plan.")
    answer: str = Field(description="The final numeric answer, digits only.")
    confidence: int = Field(
        ge=0, le=100, description="Confidence 0-100 that this answer is correct."
    )


class VerifierOutput(BaseModel):
    """Chain step 3: check the plan + answer, report a final verdict."""

    verdict: str = Field(
        description="Brief assessment of whether the answer is correct."
    )
    final_answer: str = Field(
        description="The final numeric answer — the executor's answer, or a correction."
    )
    confidence: int = Field(
        ge=0, le=100, description="Confidence 0-100 that final_answer is correct."
    )
