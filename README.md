# Evidence-Backed KPI Incident Investigator

An agentic workflow for investigating unexpected KPI changes without forcing a plausible explanation when the evidence does not justify one.

## Problem

When a business KPI such as revenue suddenly drops, analysts often inspect many correlated signals:

- traffic
- conversion rate
- pricing
- inventory
- marketing
- returns

A one-shot LLM can produce a convincing explanation even when multiple causes are equally plausible or when the observed movement is mostly noise.

This project asks a stricter question:

> What is the strongest evidence-backed explanation for the KPI incident, and should the system abstain when no dominant cause is justified?

---

## Intended Users

The intended users are:

- Data analysts
- Business analysts
- Operations teams
- Analytics teams investigating KPI incidents

---

## Core Idea

The project compares two workflows on the exact same benchmark using the same underlying LLM.

### Baseline

Gemini 2.5 Flash receives the KPI dataset and directly answers:

> Why did overall revenue drop?

The baseline uses:

- one LLM call
- the raw KPI dataset
- no executable hypothesis tests
- no evidence-ranking layer
- no deterministic verification layer

### Advanced Agentic Workflow

The advanced system separates hypothesis generation, evidence collection, review, and final verification.

It:

1. Detects the overall KPI movement.
2. Generates candidate explanations across business segments.
3. Executes mechanism-specific tests.
4. Quantifies evidence for each hypothesis.
5. Ranks competing explanations.
6. Sends structured evidence to Gemini for review.
7. Uses deterministic verification rules for the final decision.
8. Abstains when evidence does not justify one dominant explanation.

The LLM review is advisory.

The final diagnosis is controlled by the verification layer.

---

## Architecture

```text
KPI Dataset
    |
    v
Incident Detection
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
Deterministic Verifier
    |
    +------> Dominant Cause
    |
    +------> Abstain
```

---

## Supported Hypotheses

The current prototype investigates four mechanism families:

### 1. Traffic Drop

Tests whether a segment experienced a meaningful reduction in visitors.

Potential impact is estimated using:

- lost visitors
- historical conversion rate
- historical price
- number of incident days

### 2. Conversion Rate Drop

Tests whether users continued visiting but converted at a lower rate.

Potential impact is estimated using:

- post-incident visitors
- lost conversion rate
- historical price
- number of incident days

### 3. Price Drop

Tests whether lower selling prices explain lost revenue.

Potential impact is estimated using:

- units sold
- reduction in price
- number of incident days

### 4. Inventory Shortage

A decline in inventory alone is **not** treated as evidence of a shortage.

The workflow checks whether demand actually exceeded available inventory.

Inventory shortage evidence is only accepted when:

```text
orders > inventory
```

This prevents the system from treating harmless inventory movement as a root cause.

---

## Benchmark

The evaluation benchmark contains **12 controlled synthetic KPI incidents**.

The benchmark was designed to test both confident diagnosis and correct abstention.

It includes:

- clear single-cause incidents
- dominant causes with misleading signals
- multiple comparable contributors
- cases where the correct action is to abstain
- noise-only incidents
- inventory red herrings
- marketing red herrings
- competing explanations across multiple business segments

Synthetic ground truth allows the system's diagnosis to be scored deterministically.

Full benchmark design:

```text
BENCHMARK_SPEC.md
```

---

## Benchmark Cases

The 12 scenarios include several different failure modes.

```text
case_001
Single dominant inventory shortage.

case_002
Inventory shortage with misleading marketing and returns signals.

case_003
Single dominant conversion-rate collapse.

case_004
Two comparable contributors:
conversion decline + inventory shortage.
Correct behavior: abstain.

case_005
Several small contributors with no dominant cause.
Correct behavior: abstain.

case_006
Dominant traffic decline with misleading secondary signals.

case_007
Dominant price decline.

case_008
Dominant conversion-rate decline with misleading inventory movement.

case_009
Two major comparable contributors:
traffic decline + price decline.
Correct behavior: abstain.

case_010
Two comparable contributors:
inventory shortage + conversion-rate decline.
Correct behavior: abstain.

case_011
Several comparable causes with red herrings.
Correct behavior: abstain.

case_012
Noise-only scenario with misleading KPI movements.
Correct behavior: abstain.
```

---

## Primary Evaluation Metric

The primary metric is:

**Decision Accuracy**

For dominant-cause scenarios, a prediction is correct only when the system correctly identifies:

- whether it should abstain
- cause
- affected region
- affected product

For abstention scenarios, the system must explicitly return:

```json
{
  "should_abstain": true,
  "dominant_cause": null,
  "affected_region": null,
  "affected_product": null
}
```

---

## Results

### Primary Metric: Decision Accuracy

| System | Correct | Decision Accuracy |
|---|---:|---:|
| One-shot Gemini baseline | 8 / 12 | 66.67% |
| Evidence-backed workflow | 12 / 12 | 100.00% |

### Improvement

**+33.33 percentage points**

The advanced workflow corrected every benchmark error made by the baseline.

These results apply specifically to the controlled 12-case synthetic benchmark.

They are **not** a claim that the system has general 100% root-cause-analysis accuracy.

---

## Runtime and Cost

Runtime is dependent on Gemini API response latency and availability.

A representative benchmark run measured:

```text
Advanced workflow:
12/12 cases completed
Total runtime: ~148 seconds
Average runtime: ~10.3 seconds per case
```

The baseline showed substantially higher and more variable latency during
measurement, with 9/12 cases completing successfully in one run. The three
remaining cases encountered external API/network availability errors.

Because API latency and availability vary between runs, these measurements
should be treated as approximate rather than fixed performance guarantees.

Estimated Gemini API cost:

```text
Approximately $0.04 for one 12-case run of both
the baseline and advanced workflows.
```

This is an approximate estimate based on Gemini 2.5 Flash token pricing and
the project's typical prompt/output sizes. Actual cost may vary with token
usage and current API pricing.

---

## Held-Out Validation

After the development benchmark was completed, the verification rules were
frozen and two additional synthetic cases were generated with new random
seeds.

The advanced workflow correctly identified both injected mechanisms:

```text
heldout_001 → price_drop → North / Clothing
heldout_002 → traffic_drop → South / Electronics
```

Result:

```text
2 / 2 correctly identified
```

These cases are reported separately from the 12-case development benchmark and
were not used to tune the final verification thresholds.

---

## Key Baseline Failures

The baseline failed four scenarios.

### case_004

The baseline selected one cause even though two major contributors were comparable.

The advanced workflow detected competing evidence and abstained.

### case_005

The baseline selected a conversion-rate explanation despite several similarly sized contributors.

The advanced workflow found no dominant explanation and abstained.

### case_009

The baseline selected the price decline as the dominant explanation.

However, traffic decline and price decline had comparable impact.

The advanced workflow abstained.

### case_012

The baseline interpreted noisy conversion-rate movement as a meaningful root cause.

The advanced workflow applied a stricter dominance rule because the overall KPI movement was small and correctly abstained.

---

## Main Design Principle

> Correlation should generate a hypothesis, not a conclusion.

A metric change is only promoted to an explanation when the corresponding business mechanism is supported by executable evidence.

For example:

A large inventory decline may look suspicious.

However:

```text
Inventory decline != inventory shortage
```

The system checks whether inventory actually constrained demand before treating it as evidence.

---

## Abstention as a Successful Outcome

Many analytical systems are implicitly rewarded for always returning an answer.

This workflow takes a different position.

If:

- multiple explanations have comparable evidence
- overall KPI movement is very small
- evidence is inconsistent
- no mechanism clearly dominates

then the correct output may be:

```text
ABSTAIN
```

Abstention is treated as a valid analytical decision rather than a system failure.

---

## LLM Role

Gemini 2.5 Flash reviews structured evidence generated by the workflow.

The LLM is asked to assess:

1. Which hypotheses have meaningful executable evidence?
2. Are multiple explanations comparable?
3. Does one explanation clearly dominate?
4. Should the system be cautious?

However, Gemini does **not** make the final decision.

The review is advisory.

The deterministic verifier controls the final output.

This prevents a persuasive LLM explanation from overriding contradictory evidence.

---

## Deterministic Verification

The verifier compares the strongest candidate against competing explanations.

General rule:

```text
dominant candidate share >= 60%
```

For small overall KPI movements:

```text
overall decline < 5%
```

the system requires stronger evidence:

```text
dominant candidate share >= 80%
```

Otherwise, the workflow abstains.

This stricter rule helps prevent normal noise from being promoted into a confident root-cause claim.

---

## Example: Dominant Cause

For `case_001`, the evidence system identifies:

```text
Cause: inventory_shortage
Region: South
Product: Electronics
Impact Share: 100%
```

Final decision:

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

---

## Example: Multi-Causal Incident

For `case_004`, the strongest candidates are approximately:

```text
North / Electronics
conversion_rate_drop
Impact Share: ~49%

South / Clothing
inventory_shortage
Impact Share: ~47%
```

Neither explanation dominates.

Final decision:

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

---

## Example: Noise Case

For `case_012`, several conversion changes appear in the data.

However:

- overall revenue decline is only around 4%
- multiple weak explanations compete
- no single mechanism satisfies the stricter dominance threshold

Final decision:

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

---

## Project Structure

```text
kpi-incident-investigator/
|
|-- advanced/
|   |-- advanced_agent.py
|   `-- run_all_advanced.py
|
|-- baseline/
|   |-- baseline_agent.py
|   |-- run_all_baseline.py
|   `-- test_gemini.py
|
|-- benchmark/
|   |
|   |-- cases/
|   |   |-- case_001/
|   |   |-- case_002/
|   |   |-- ...
|   |   `-- case_012/
|   |
|   |-- create_heldout.py
|   |-- heldout/
|   |   |-- heldout_001/
|   |   `-- heldout_002/
|   |
|   |-- predictions/
|   |   |-- baseline/
|   |   `-- advanced/
|   |
|   |-- evaluate.py
|   |-- evaluate_all.py
|   |-- evaluate_advanced.py
|   `-- generate_benchmark.py
|
|-- trajectories/
|   |-- README.md
|   |-- case_001_advanced_trace.txt
|   |-- case_001_prediction.json
|   |-- case_004_advanced_trace.txt
|   |-- case_004_baseline_prediction.json
|   |-- case_004_baseline_trace.txt
|   |-- case_004_prediction.json
|   |-- case_012_advanced_trace.txt
|   `-- case_012_prediction.json
|
|-- app.py
|-- BENCHMARK_SPEC.md
|-- CHANGELOG.md
|-- requirements.txt
`-- README.md
```

---

## Requirements

The project requires:

```text
Python 3.x
pandas
numpy
google-genai
streamlit
```

---

## Installation

Clone the repository and enter the project directory.

```powershell
git clone https://github.com/saurabh2141/kpi-incident-investigator.git
cd kpi-incident-investigator
```

Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

---

## Gemini API Key

The Gemini API key must be supplied through an environment variable.

### PowerShell

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
```

Do not commit the API key to the repository.

---

## Launch the Demo UI

The project includes a Streamlit interface for interactively exploring the benchmark incidents.

Run:

```powershell
py -m streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

The interface allows you to:

- select any benchmark incident
- inspect the KPI revenue movement
- compare the one-shot baseline diagnosis
- run the evidence-backed investigation live
- inspect ranked evidence
- read the Gemini evidence review
- view the final verified diagnosis or abstention decision

For a representative demo, use:

```text
case_004
```

In this scenario, the baseline selects a single inventory-shortage explanation, while the advanced workflow finds two comparable contributors and correctly abstains.

## Run a Single Baseline Investigation

Example:

```powershell
py baseline/baseline_agent.py --data benchmark/cases/case_001/data.csv --scenario-id case_001 --output benchmark/predictions/baseline_case_001.json
```

---

## Run the Full Baseline Benchmark

```powershell
py baseline/run_all_baseline.py
```

The predictions are written to:

```text
benchmark/predictions/baseline/
```

---

## Evaluate the Baseline

Run:

```powershell
py benchmark/evaluate_all.py
```

Measured result:

```text
Correct: 8/12
Decision Accuracy: 66.67%
```

---

## Run a Single Advanced Investigation

Example:

```powershell
py advanced/advanced_agent.py --data benchmark/cases/case_001/data.csv --scenario-id case_001 --output benchmark/predictions/advanced_case_001.json
```

The workflow prints:

```text
TOP EVIDENCE CANDIDATES
GEMINI EVIDENCE REVIEW
FINAL VERIFIED DECISION
```

---

## Run the Full Advanced Benchmark

```powershell
py advanced/run_all_advanced.py
```

Predictions are written to:

```text
benchmark/predictions/advanced/
```

---

## Evaluate the Advanced Workflow

Run:

```powershell
py benchmark/evaluate_advanced.py
```

Expected result:

```text
case_001 CORRECT
case_002 CORRECT
case_003 CORRECT
case_004 CORRECT
case_005 CORRECT
case_006 CORRECT
case_007 CORRECT
case_008 CORRECT
case_009 CORRECT
case_010 CORRECT
case_011 CORRECT
case_012 CORRECT

========================================
ADVANCED BENCHMARK RESULT
========================================
Correct: 12/12
Decision Accuracy: 100.00%
```

---

## Evaluate a Single Prediction

A prediction can also be scored individually.

Example:

```powershell
py benchmark/evaluate.py --ground-truth benchmark/cases/case_004/ground_truth.json --prediction benchmark/predictions/advanced/case_004.json
```

Example output:

```text
EVALUATION RESULT
-----------------

decision_correct: true
abstention_correct: true

PRIMARY DECISION: CORRECT
```

---

## Fair Baseline Comparison

Both systems use:

```text
gemini-2.5-flash
```

Both systems are evaluated on:

```text
the exact same 12 benchmark cases
```

The model itself is therefore held constant.

The main experimental variable is the workflow.

### Baseline

```text
Dataset
   |
   v
Gemini
   |
   v
Diagnosis
```

### Advanced

```text
Dataset
   |
   v
Hypothesis Generation
   |
   v
Mechanism Tests
   |
   v
Evidence Ranking
   |
   v
Gemini Review
   |
   v
Deterministic Verification
   |
   v
Diagnosis / Abstention
```

This helps isolate whether better process design improves analytical reliability.

---

## Experiment History

Detailed experiment history is available in:

```text
CHANGELOG.md
```

The changelog includes:

- baseline design
- benchmark result
- observed failures
- advanced workflow changes
- rejected approaches
- final benchmark result

---

## Rejected Approach

A raw metric movement was initially considered potential evidence.

That idea was rejected.

For example:

```text
Inventory decreased
```

does not necessarily mean:

```text
Inventory shortage caused revenue loss
```

The advanced workflow instead checks:

```text
Did available inventory actually constrain demand?
```

Only then can the inventory hypothesis receive causal-style mechanism evidence.

---

## Reproducibility

The benchmark uses deterministic synthetic scenarios with stored ground-truth files.

Each case contains:

```text
data.csv
ground_truth.json
```

Predictions are evaluated using deterministic Python scoring logic.

This makes the baseline and advanced results directly reproducible.

---

## Ground Truth

Ground truth specifies information such as:

```text
scenario_id
should_abstain
dominant_cause
affected_region
affected_product
expected_impact
```

For multi-causal and noise scenarios:

```text
should_abstain = true
```

---

## Why Synthetic Data?

Synthetic data was selected intentionally.

It provides known incident mechanisms.

This allows the evaluation to answer:

> Did the system actually identify the mechanism that generated the KPI incident?

instead of relying on subjective human judgment about an unknown real-world cause.

It also allows deliberate creation of difficult scenarios such as:

- red herrings
- competing explanations
- noise
- false correlations
- multi-causal incidents

---

## Limitations

This prototype uses controlled synthetic data and a fixed set of supported mechanisms.

It does not claim formal causal inference.

The current workflow assumes:

- a known incident start date
- structured tabular KPI data
- defined business segments
- four supported mechanism families

A production version would require:

- broader hypothesis generation
- domain-specific metrics
- longer historical windows
- seasonality handling
- trend decomposition
- external-event evidence
- confidence calibration
- missing-data handling
- anomaly detection
- more sophisticated counterfactual estimation
- additional data sources

---

## Future Work

Potential extensions include:

### Dynamic Hypothesis Generation

Allow the agent to propose new mechanism tests instead of relying on four predefined families.

### SQL / Warehouse Tools

Allow the agent to query production analytical databases directly.

### External Evidence

Connect:

- deployment logs
- marketing systems
- pricing systems
- inventory systems
- incident logs

### Time-Series Models

Improve expected KPI baselines using:

- seasonality
- trends
- forecasting
- anomaly detection

### Confidence Calibration

Estimate how reliable each diagnosis is instead of relying only on impact-share thresholds.

### Analyst Interaction

Allow an analyst to ask:

```text
Why did you reject inventory shortage?

What evidence supports conversion decline?

What would change your conclusion?
```

---

## Hot Take

> A useful analytical agent should not be rewarded simply for always producing an answer.

In high-ambiguity KPI investigations, knowing when the evidence is insufficient is part of the intelligence of the system.

A plausible explanation is not necessarily a justified explanation.

The system should earn the right to make a confident claim through evidence.

---

## Final Result

```text
Baseline Decision Accuracy
8 / 12
66.67%

Advanced Decision Accuracy
12 / 12
100.00%

Improvement
+33.33 percentage points
```

The main improvement did not come from using a larger model.

It came from changing the workflow:

```text
Plausible answer
        |
        v
Evidence-backed hypothesis
        |
        v
Executable mechanism test
        |
        v
Competing evidence comparison
        |
        v
Verified conclusion
        OR
        v
Abstention
```

That is the central idea behind the Evidence-Backed KPI Incident Investigator.