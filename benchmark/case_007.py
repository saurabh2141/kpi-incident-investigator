import json
from pathlib import Path

from generate_benchmark import (
    generate_base_data,
    inject_price_drop,
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SEED = 294
INCIDENT_START = "2026-08-15"

OUTPUT_DIR = Path("benchmark/cases/case_007")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Generate normal business data
# ---------------------------------------------------------

df = generate_base_data(seed=SEED)


# ---------------------------------------------------------
# TRUE CAUSE
# ---------------------------------------------------------
# Price for South / Electronics falls by 50%.
#
# Traffic, conversion and inventory are left unchanged.
# Therefore the revenue decline should be attributable
# to the price reduction.
# ---------------------------------------------------------

df, expected_impact = inject_price_drop(
    df=df,
    region="South",
    product="Electronics",
    incident_start=INCIDENT_START,
    multiplier=0.50,
)


# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

data_path = OUTPUT_DIR / "data.csv"

df.to_csv(
    data_path,
    index=False
)


# ---------------------------------------------------------
# Save ground truth
# ---------------------------------------------------------

ground_truth = {
    "scenario_id": "case_007",
    "scenario_type": "single_dominant_cause",

    "user_question": (
        "Why did overall revenue drop after 2026-08-15?"
    ),

    "target_kpi": "revenue",
    "direction": "decrease",

    "dominant_cause": "price_drop",
    "affected_region": "South",
    "affected_product": "Electronics",

    "incident_start": INCIDENT_START,

    "should_abstain": False,

    "expected_impact": float(expected_impact),

    "random_seed": SEED,
}


ground_truth_path = OUTPUT_DIR / "ground_truth.json"

with open(ground_truth_path, "w") as f:
    json.dump(
        ground_truth,
        f,
        indent=4
    )


print("Case 007 generated successfully.")
print(f"Dataset saved to: {data_path}")
print(f"Ground truth saved to: {ground_truth_path}")
print(f"Injected revenue impact: {expected_impact:.2f}")