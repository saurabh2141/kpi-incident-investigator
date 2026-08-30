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


## Held-Out Validation

After the 12-case development benchmark and verifier thresholds were frozen,
two additional synthetic cases were generated with new random seeds.

These cases were not used to tune the verification rules.

### heldout_001

```text
Injected cause: price_drop
Segment: North / Clothing
Result: Correct
```

The workflow ranked the price-drop hypothesis first and correctly identified
the injected cause despite additional competing signals.

### heldout_002

```text
Injected cause: traffic_drop
Segment: South / Electronics
Result: Correct
```

The workflow identified the injected traffic-drop mechanism and correctly
reported the affected segment.

Held-out validation result:

```text
2 / 2 correctly identified
```

This validation is reported separately from the 12-case development benchmark.
It is intended as a small generalization sanity check rather than a second
benchmark.


## Runtime Measurement

Runtime instrumentation was added to the baseline and advanced benchmark
runners without changing the investigation logic.

Observed measurement:

```text
Advanced: ~148 seconds for 12 cases
Advanced average: ~10.3 seconds per case
```

The baseline measurement was affected by external API and network availability
errors, so its timing is reported qualitatively rather than as a directly
comparable benchmark.

Runtime is API-dependent and may vary between runs.


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