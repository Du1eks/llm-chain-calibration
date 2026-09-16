"""Thin wrapper around the Claude API: one structured call + cost tracking.

Everything else in this project (single-shot, planner, executor, verifier)
goes through call_structured() so cost accounting and error handling live
in exactly one place.
"""

import os

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

from config import config

load_dotenv()

_client = None


def get_client() -> anthropic.Anthropic:
    """Lazily construct the Anthropic client (reads ANTHROPIC_API_KEY)."""
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Create a .env file "
                "(see .env.example) with your key."
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


class CostTracker:
    """Accumulates token usage across calls and enforces a hard USD ceiling.

    Pass the same tracker instance into every call_structured() call
    during a run (a pilot, a probe, the full experiment) so spend adds
    up across the whole run, not per call.
    """

    def __init__(self, max_spend_usd: float = config.MAX_SPEND_USD):
        self.max_spend_usd = max_spend_usd
        self.input_tokens = 0
        self.output_tokens = 0
        self.n_calls = 0

    @property
    def cost_usd(self) -> float:
        input_cost = self.input_tokens / 1_000_000 * config.PRICE_PER_MTOK_INPUT
        output_cost = self.output_tokens / 1_000_000 * config.PRICE_PER_MTOK_OUTPUT
        return input_cost + output_cost

    def record(self, usage) -> None:
        self.input_tokens += usage.input_tokens
        self.output_tokens += usage.output_tokens
        self.n_calls += 1
        if self.cost_usd > self.max_spend_usd:
            raise RuntimeError(
                f"Budget guard tripped: ${self.cost_usd:.4f} spent "
                f"(limit ${self.max_spend_usd:.2f}) after {self.n_calls} calls. "
                "Raise config.MAX_SPEND_USD if this is expected."
            )

    def summary(self) -> str:
        return (
            f"{self.n_calls} calls, {self.input_tokens} in / "
            f"{self.output_tokens} out tokens, ${self.cost_usd:.4f}"
        )


def call_structured(
    system: str,
    user: str,
    output_format: type[BaseModel],
    tracker: CostTracker | None = None,
):
    """Make one Claude call and parse the response into output_format.

    Returns (parsed, usage) — parsed is a validated instance of
    output_format, usage is the raw usage object from the response
    (already folded into tracker if one was passed).
    """
    client = get_client()
    try:
        response = client.messages.parse(
            model=config.MODEL_ID,
            max_tokens=config.MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_format=output_format,
            # temperature is no longer a typed param in this SDK version
            # (1.6.0+) but the server still accepts it for Haiku 4.5 —
            # pass it through raw. See docs/napredak_projekta.md for why.
            extra_body={"temperature": config.TEMPERATURE},
        )

    except anthropic.RateLimitError as e:
        raise RuntimeError(f"Rate limited by Claude API: {e}") from e
    except anthropic.AuthenticationError as e:
        raise RuntimeError(
            "Claude API authentication failed — check ANTHROPIC_API_KEY in .env"
        ) from e
    except anthropic.APIStatusError as e:
        raise RuntimeError(f"Claude API error ({e.status_code}): {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise RuntimeError(f"Network error calling Claude API: {e}") from e

    if tracker is not None:
        tracker.record(response.usage)

    return response.parsed_output, response.usage
