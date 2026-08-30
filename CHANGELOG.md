# Experiment Changelog

## Baseline — One-Shot LLM Diagnosis

Approach:
- Gemini 2.5 Flash receives the KPI dataset directly.
- One prompt asks it to identify the dominant explanation or abstain.
- No executable mechanism tests.
- No deterministic verification layer.

Benchmark result:
- Correct: 8 / 12
- Decision Accuracy: 66.67%

Observed failures:
- case_004: selected one cause despite two comparable contributors.
- case_005: selected a cause when no dominant contributor existed.
- case_009: selected one cause despite two comparable contributors.
- case_012: attributed normal/noisy variation to a conversion-rate decline.

Key failure mode:
The LLM can turn a plausible correlation into a confident explanation even when
the evidence does not justify one dominant cause.


## Advanced — Evidence-Backed Incident Investigator

Changes:
- Generate explicit hypotheses for traffic, conversion, price, and inventory.
- Test each hypothesis against before/after segment data.
- Inventory shortage is only considered evidence when inventory actually
  constrains demand.
- Estimate impact for each supported mechanism.
- Compare competing explanations using evidence shares.
- Use an LLM to review the structured evidence.
- Keep the LLM review advisory.
- Use deterministic verification rules for the final decision.
- Abstain when no explanation dominates.
- Apply stricter dominance requirements for small overall KPI movements.

Benchmark result:
- Correct: 12 / 12
- Decision Accuracy: 100.00%
- Improvement over baseline: +33.33 percentage points.

Previously failed cases corrected:
- case_004
- case_005
- case_009
- case_012


## Iteration Log

### Iteration 1 — One-Shot Baseline

The initial baseline used a single Gemini call to diagnose the KPI incident.

Result:

- 8 / 12 correct
- Decision Accuracy: 66.67%

Observed failures:

- case_004: selected one cause despite two comparable contributors
- case_005: selected a cause when no dominant contributor existed
- case_009: selected one cause despite two comparable contributors
- case_012: treated noisy variation as a meaningful conversion-rate decline

Decision:

The baseline showed that a plausible LLM explanation was not sufficient for
ambiguous KPI incidents.

### Iteration 2 — Mechanism-Specific Evidence

Added executable tests for:

- traffic
- conversion rate
- price
- inventory

The inventory test was made more specific: inventory movement is not treated
as evidence unless demand actually exceeds available inventory.

Decision:

Use mechanism-level evidence instead of raw metric correlation.

### Iteration 3 — Evidence Ranking and Comparison

Added impact estimates and impact shares so competing explanations could be
compared directly.

This exposed cases such as case_004, where two explanations had nearly equal
contributions.

Decision:

Do not promote the highest-ranked candidate automatically when competing
evidence is comparable.

### Iteration 4 — Deterministic Verification

Added a deterministic verification layer after the Gemini evidence review.

The LLM review is advisory; the verifier applies the dominance rules and can
reject a diagnosis proposed by the model.

Decision:

Make the final output either a verified dominant cause or an explicit
abstention.

### Iteration 5 — Final Benchmark Validation

Final result:

```text
Baseline:  8 / 12
Advanced: 12 / 12
Improvement: +33.33 percentage points
```

All 12 advanced benchmark cases were evaluated correctly.

The main improvement came from combining executable mechanism tests,
competing-evidence comparison, and deterministic verification rather than
relying on a one-shot LLM explanation.


## Removed / Rejected Approach

A raw metric change alone was rejected as evidence of root cause.

For example, falling inventory can look suspicious, but it is not an inventory
shortage unless available inventory actually constrains orders. The advanced
workflow therefore checks the mechanism instead of treating correlation as
proof.


## Main Takeaway

Correlation should generate a hypothesis, not a conclusion.

The system should only make a dominant-cause claim when executable evidence
supports it strongly enough. Otherwise, abstention is a successful outcome.