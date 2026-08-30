# Evidence-Backed KPI Incident Investigator
## Benchmark Specification

## 1. Intended User

Business analysts, data analysts, and operations teams who need to investigate
unexpected changes in business KPIs.

Examples:

- Revenue suddenly drops
- Conversion rate falls
- Returns increase
- Orders decrease
- Average order value changes unexpectedly

---

## 2. Problem

When a KPI suddenly changes, analysts often manually investigate many possible
causes such as:

- Region
- Product
- Marketing
- Traffic
- Conversion
- Pricing
- Discounts
- Inventory
- Returns

Several factors may change at the same time.

A simple AI agent may find a correlation and confidently claim that it is the
root cause even when the evidence is weak.

The goal of this project is to build an agent that investigates competing
hypotheses, tests them against data, verifies the evidence, and either:

1. Reports the strongest evidence-backed explanation, or
2. Abstains when there is not enough evidence for a dominant explanation.

---

## 3. Primary Metric

### Decision Accuracy

A benchmark case is considered correct when the system:

- Identifies the injected dominant cause correctly, OR
- Correctly abstains when no dominant cause exists.

Formula:

Decision Accuracy = Correct Decisions / Total Benchmark Cases

---

## 4. Secondary Metrics

The current benchmark is scored primarily using Decision Accuracy.

Additional diagnostic quantities recorded or considered during development include:

- impact estimates
- abstention behavior
- evidence dominance
- execution success
- approximate investigation cost

These are supporting diagnostics rather than the primary benchmark score.

---

## 5. Benchmark Scenario Types

### Scenario A — Single Dominant Cause

One factor clearly explains most of the KPI change.

Example:

Revenue falls because Electronics inventory drops sharply in the South region.

Expected result:

The system identifies the Electronics inventory shortage in the South region.

---

### Scenario B — Dominant Cause With Red Herrings

One true dominant cause exists, but several unrelated metrics also change.

Example:

True cause:

Electronics inventory shortage in South.

Red herrings:

- Marketing spend decreases slightly
- Returns increase slightly
- North-region traffic decreases
- Discounts change slightly

Expected result:

The system identifies the inventory shortage and does not incorrectly select
the red herrings.

---

### Scenario C — Multiple Contributing Causes

Several real factors contribute to the KPI change.

Example:

Revenue decreases because:

- conversion rate falls in one segment
- inventory constrains demand in another segment
- traffic also declines

Expected result:

The system recognizes that multiple mechanisms contributed and does not falsely attribute the entire change to one factor.

---

### Scenario D — No Dominant Cause / Abstention

The KPI movement results from several small changes or normal noise.

No factor provides enough evidence to confidently identify one dominant cause.

Expected result:

The system should abstain from declaring one root cause.

It may report possible contributors, but must clearly state that the evidence
does not support a dominant explanation.

---

## 6. Benchmark Size

Benchmark composition:

- 3 Single Dominant Cause cases
- 3 Red-Herring cases
- 3 Multiple-Contributor cases
- 3 Abstention cases

Total:

12 benchmark cases

The benchmark uses fixed synthetic scenarios so the same datasets and ground truth can be reproduced.

---

## 7. Dataset Schema

The synthetic benchmark uses structured KPI data with fields such as:

- date
- region
- product
- visitors
- conversion_rate
- orders
- units_sold
- price
- inventory
- marketing_spend
- returns
- revenue

Some scenarios omit or vary non-essential fields depending on the mechanism being tested.

Only fields relevant to the benchmark scenarios are included.

---

## 8. Ground Truth

Every benchmark case contains structured ground truth stored in:

```text
benchmark/cases/<case_id>/ground_truth.json
```

Ground-truth fields include:

```text
scenario_id
scenario_type
target_kpi
direction
dominant_cause
affected_region
affected_product
should_abstain
expected_impact
```

For example, a dominant-cause case may specify:

```json
{
  "scenario_id": "case_001",
  "dominant_cause": "inventory_shortage",
  "affected_region": "South",
  "affected_product": "Electronics",
  "should_abstain": false,
  "expected_impact": 68900.0
}
```

For multi-causal or noise-oriented cases, the benchmark instead requires abstention:

```json
{
  "scenario_id": "case_012",
  "dominant_cause": null,
  "should_abstain": true
}
```

Ground truth is used only by the evaluator and is never passed to the investigating workflow.

---

## 9. Fair Comparison Rule

The baseline and advanced system must receive:

- The same dataset
- The same investigation objective
- The same benchmark cases
- The same underlying LLM: Gemini 2.5 Flash
- Equivalent access to the data

The main difference should be the investigation architecture.

---

## 10. Baseline Workflow

The implemented baseline uses:

```text
User Question
→ Inspect Dataset
→ One Gemini Analysis
→ Final Diagnosis or Abstention
```

The baseline intentionally has no executable mechanism tests, no evidence-ranking layer, and no deterministic verifier.

Its purpose is to represent a reasonable one-shot LLM approach for the same KPI investigation task.

---

## 11. Advanced Workflow

The implemented advanced workflow uses:

```text
KPI Change
→ Generate Competing Hypotheses
→ Execute Mechanism Tests
→ Rank Evidence
→ Gemini Evidence Review
→ Deterministic Verification
→ Report Dominant Cause or Abstain
```

The advanced workflow tests traffic, conversion-rate, price, and inventory mechanisms across business segments.

Gemini reviews the structured evidence, but the final decision is controlled by deterministic verification rules.

---

## 12. Main Failure Mode

The main failure mode evaluated by the benchmark is:

"A plausible correlation is mistaken for the actual explanation."

The benchmark tests whether the system:

- Selects misleading signals
- Makes unsupported claims
- Ignores competing explanations
- Refuses to abstain when evidence is insufficient

The advanced workflow is evaluated on whether it reduces these failures relative to the baseline.