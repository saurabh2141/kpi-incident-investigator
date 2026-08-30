import json
from pathlib import Path

from generate_benchmark import (
    generate_base_data,
    inject_inventory_shortage,
    inject_conversion_drop,
)


SEED = 420
INCIDENT_START = "2026-08-15"

OUTPUT_DIR = Path("benchmark/cases/case_010")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Generate normal business data
# ---------------------------------------------------------

df = generate_base_data(seed=SEED)


# ---------------------------------------------------------
# Contributor 1: Inventory shortage
# South / Electronics
# ---------------------------------------------------------

df, inventory_impact = inject_inventory_shortage(
    df=df,
    seed=421,
    region="South",
    product="Electronics",
    incident_start=INCIDENT_START,
    low=25,
    high=35,
)


# ---------------------------------------------------------
# Contributor 2: Conversion-rate drop
# North / Clothing
# ---------------------------------------------------------

df, conversion_impact = inject_conversion_drop(
    df=df,
    seed=422,
    region="North",
    product="Clothing",
    incident_start=INCIDENT_START,
    low=0.012,
    high=0.018,
)


# ---------------------------------------------------------
# Calculate combined impact
# ---------------------------------------------------------

total_expected_impact = (
    inventory_impact
    + conversion_impact
)

inventory_share = (
    inventory_impact
    / total_expected_impact
)

conversion_share = (
    conversion_impact
    / total_expected_impact
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
    "scenario_id": "case_010",
    "scenario_type": "multiple_contributing_causes",

    "user_question": (
        "Why did overall revenue drop after 2026-08-15?"
    ),

    "target_kpi": "revenue",
    "direction": "decrease",

    "dominant_cause": None,
    "should_abstain": True,

    "expected_behavior": (
        "Report both material contributors and abstain "
        "from declaring one dominant root cause."
    ),

    "contributors": [
        {
            "cause": "inventory_shortage",
            "region": "South",
            "product": "Electronics",
            "expected_impact": float(inventory_impact),
            "impact_share": float(inventory_share),
        },
        {
            "cause": "conversion_rate_drop",
            "region": "North",
            "product": "Clothing",
            "expected_impact": float(conversion_impact),
            "impact_share": float(conversion_share),
        },
    ],

    "total_expected_impact": float(total_expected_impact),
    "incident_start": INCIDENT_START,
    "random_seed": SEED,
}


ground_truth_path = OUTPUT_DIR / "ground_truth.json"

with open(ground_truth_path, "w") as f:
    json.dump(
        ground_truth,
        f,
        indent=4
    )


print("Case 010 generated successfully.")
print(f"Dataset saved to: {data_path}")
print(f"Ground truth saved to: {ground_truth_path}")
print()
print(f"Inventory impact:  {inventory_impact:.2f}")
print(f"Conversion impact: {conversion_impact:.2f}")
print(f"Combined impact:   {total_expected_impact:.2f}")
print()
print(f"Inventory share:  {inventory_share * 100:.2f}%")
print(f"Conversion share: {conversion_share * 100:.2f}%")