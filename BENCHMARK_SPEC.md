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

We may additionally measure:

- False Attribution Rate
- Correct Abstention Rate
- Impact Estimation Error
- Unsupported Claim Rate
- Execution Success Rate
- Investigation Latency
- Approximate LLM Cost

The primary metric remains Decision Accuracy.

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

- Conversion falls
- Inventory availability falls
- Returns increase

Expected result:

The system recognizes that several factors contributed and does not falsely
attribute the entire change to one factor.

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

Initial benchmark:

- 3 Single Dominant Cause cases
- 3 Red-Herring cases
- 3 Multiple-Contributor cases
- 3 Abstention cases

Total:

12 benchmark cases

Every case will use a fixed random seed so the exact datasets can be reproduced.

---

## 7. Initial Dataset Schema

Each synthetic dataset may contain:

- date
- region
- product
- channel
- visitors
- orders
- units_sold
- price
- discount
- inventory
- returns
- marketing_spend
- revenue

We will avoid adding unnecessary columns.

---

## 8. Ground Truth

Every benchmark case must have structured ground truth.

Example:

{
    "scenario_id": "case_001",
    "scenario_type": "red_herring",
    "target_kpi": "revenue",
    "direction": "decrease",
    "dominant_cause": "inventory_shortage",
    "affected_region": "South",
    "affected_product": "Electronics",
    "should_abstain": false,
    "expected_impact": 1250000
}

Example abstention case:

{
    "scenario_id": "case_010",
    "scenario_type": "no_dominant_cause",
    "target_kpi": "revenue",
    "dominant_cause": null,
    "should_abstain": true
}

---

## 9. Fair Comparison Rule

The baseline and advanced system must receive:

- The same dataset
- The same user question
- The same benchmark cases
- The same underlying LLM where possible
- Equivalent access to the data

The main difference should be the investigation architecture.

---

## 10. Baseline Concept

The baseline will eventually use:

User Question
→ Inspect Data
→ Perform One Analysis Attempt
→ Produce Final Explanation

Do not implement yet.

---

## 11. Advanced Workflow Concept

The advanced system will eventually use:

KPI Change
→ Generate Competing Hypotheses
→ Test Hypotheses
→ Reject Unsupported Hypotheses
→ Verify Strongest Explanation
→ Report Evidence or Abstain

Do not implement yet.

---

## 12. Main Failure Mode

The main failure mode we want to investigate is:

"A plausible correlation is mistaken for the actual explanation."

The benchmark should therefore test whether the system:

- Selects misleading signals
- Makes unsupported claims
- Ignores competing explanations
- Refuses to abstain when evidence is insufficient

The advanced workflow should reduce these failures compared with the baseline.