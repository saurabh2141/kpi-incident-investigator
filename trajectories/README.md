# Agent Trajectories

This folder contains real execution traces captured from the KPI Incident
Investigator.

The traces are included to make the agent workflow inspectable and reproducible.

No trajectories were manually fabricated.

---

## Case 001 — Clear Dominant Cause

Files:

```text
case_001_advanced_trace.txt
case_001_prediction.json
```

Purpose:

Demonstrates that the advanced workflow does not abstain unnecessarily.

The evidence identifies:

```text
Cause: inventory_shortage
Region: South
Product: Electronics
Evidence Share: 100%
```

Final verified decision:

```json
{
  "scenario_id": "case_001",
  "should_abstain": false,
  "dominant_cause": "inventory_shortage",
  "affected_region": "South",
  "affected_product": "Electronics",
  "estimated_impact": 68900.0
}
```

This trajectory demonstrates the workflow's ability to make a confident
diagnosis when one explanation clearly dominates.

---

## Case 004 — Baseline Failure vs Evidence-Backed Workflow

### Baseline Files

```text
case_004_baseline_trace.txt
case_004_baseline_prediction.json
```

### Advanced Files

```text
case_004_advanced_trace.txt
case_004_prediction.json
```

Case 004 contains two comparable contributors.

The one-shot baseline selected:

```text
inventory_shortage
South / Clothing
```

and returned a non-abstaining diagnosis.

However, the advanced workflow executed mechanism-specific evidence tests and
found approximately:

```text
conversion_rate_drop
North / Electronics
Impact Share: 49.1%

inventory_shortage
South / Clothing
Impact Share: 47.2%
```

Neither explanation clearly dominated.

Final advanced decision:

```json
{
  "scenario_id": "case_004",
  "should_abstain": true,
  "dominant_cause": null,
  "affected_region": null,
  "affected_product": null,
  "estimated_impact": null
}
```

This trajectory demonstrates the main failure mode addressed by the project:

> A plausible explanation should not automatically become a confident
> conclusion when competing evidence is similarly strong.

---

## Case 012 — LLM Review vs Deterministic Verification

Files:

```text
case_012_advanced_trace.txt
case_012_prediction.json
```

Case 012 is a noise-oriented scenario with a relatively small overall KPI
movement.

The evidence system produced several conversion-rate hypotheses:

```text
South / Electronics: 54.09%
North / Electronics: 34.18%
South / Clothing: 11.73%
```

During this run, the Gemini evidence reviewer suggested that the evidence was
strong enough not to abstain.

However, the deterministic verifier applies a stricter dominance requirement
when the overall KPI movement is small.

The leading candidate did not satisfy that requirement.

Final verified decision:

```json
{
  "scenario_id": "case_012",
  "should_abstain": true,
  "dominant_cause": null,
  "affected_region": null,
  "affected_product": null,
  "estimated_impact": null
}
```

This trajectory demonstrates that the LLM is advisory rather than authoritative.

The final decision remains constrained by executable evidence and deterministic
verification rules.

---

## Workflow Represented by the Traces

```text
KPI Dataset
    |
    v
Hypothesis Generation
    |
    v
Executable Mechanism Tests
    |
    v
Evidence Ranking
    |
    v
Gemini Evidence Review
    |
    v
Deterministic Verification
    |
    +------> Dominant Cause
    |
    +------> Abstain
```

---

## Why These Three Cases?

Together, these trajectories demonstrate three distinct system behaviors:

```text
case_001
Strong single cause
→ Diagnose

case_004
Multiple comparable causes
→ Abstain

case_012
LLM favors a conclusion but verification threshold is not met
→ Override LLM and abstain
```

The trajectories therefore show that the system neither blindly follows the
LLM nor blindly abstains.

Its final behavior depends on the strength and dominance of executable
evidence.