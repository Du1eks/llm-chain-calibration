from pathlib import Path

# --- Model ---
MODEL_ID = "claude-haiku-4-5"
TEMPERATURE = 0.0  # deterministic — needed for reproducibility
MAX_TOKENS = 2048  # enough for GSM8K reasoning + JSON output

# Haiku 4.5 pricing, USD per 1M tokens (input, output).
# Source: Anthropic pricing page, checked 2026-09-16.
PRICE_PER_MTOK_INPUT = 1.00
PRICE_PER_MTOK_OUTPUT = 5.00

# --- Sampling ---
SAMPLE_SIZE = 100
RANDOM_SEED = 42

# --- Budget guard ---
# Hard stop enforced by CostTracker in src/utils/llm.py. Pilots and the
# full run should stay well under this — see docs/napredak_projekta.md
# for measured actual costs.
MAX_SPEND_USD = 3.00

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_RESULTS = PROJECT_ROOT / "data" / "results"
FIGURES = PROJECT_ROOT / "results" / "figures"

# --- GSM8K source ---
GSM8K_URL = (
    "https://raw.githubusercontent.com/openai/grade-school-math/master/"
    "grade_school_math/data/test.jsonl"
)
GSM8K_RAW_FILE = DATA_RAW / "gsm8k_test.jsonl"
