# LLM Chain Calibration

Does a multi-agent pipeline systematically overestimate its own reliability
compared to a single model call on the same task?

## Status

**Phase 0 — planning.** See [`docs/plan_projekta.md`](docs/plan_projekta.md)
for the full research plan, scope decisions and week-by-week timeline
(in Serbian; the code, prompts and results will be in English).

## Idea

When a model solves a problem on its own and reports how confident it is in
the answer, that confidence is usually reasonably well calibrated — if it
says 80%, it tends to be right about 80% of the time. This project tests
whether that calibration breaks down when the same problem is solved not by
one model call but by a three-agent chain (Planner → Executor → Verifier),
where each step inherits the previous step's errors while still reporting
high confidence.

## Method (planned)

- **Task domain:** GSM8K math problems (~100 problems), auto-gradable.
- **Condition A — single-shot:** one call, model solves the problem and
  reports confidence (0–100%) in the same response.
- **Condition B — chain:** Planner breaks the problem down, Executor
  carries out the plan, Verifier checks the result — each stage reports its
  own confidence.
- **Metrics:** Expected Calibration Error (ECE), Brier score, reliability
  diagrams, comparing ECE(single-shot) vs ECE(chain).

Full details, including why this scope and what counts as a minimal viable
result, are in [`docs/plan_projekta.md`](docs/plan_projekta.md).
