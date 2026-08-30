import json
from pathlib import Path

from generate_benchmark import (
    generate_base_data,
    inject_traffic_drop,
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SEED = 252
INCIDENT_START = "2026-08-15"

OUTPUT_DIR = Path("benchmark/cases/case_006")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Generate normal data
# ---------------------------------------------------------

df = generate_base_data(seed=SEED)


# ---------------------------------------------------------
# TRUE CAUSE
# ---------------------------------------------------------
# Traffic falls sharply for South / Clothing.
# This is the actual cause we expect the investigator to find.
# ---------------------------------------------------------

df, expected_impact = inject_traffic_drop(
    df=df,
    region="South",
    product="Clothing",
    incident_start=INCIDENT_START,
    multiplier=0.50,
)


# ---------------------------------------------------------
# RED HERRING 1
# ---------------------------------------------------------
# Marketing spend falls sharply in North / Electronics.
#
# Marketing spend does not mechanically drive visitors
# in this benchmark, so this should NOT be blamed for
# the revenue incident.
# ---------------------------------------------------------

marketing_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "North")
    & (df["product"] == "Electronics")
)

df.loc[
    marketing_mask,
    "marketing_spend"
] *= 0.55


# ---------------------------------------------------------
# RED HERRING 2
# ---------------------------------------------------------
# Returns increase in North / Clothing.
#
# Revenue is gross sales revenue in this benchmark,
# so this change should not explain the target KPI drop.
# ---------------------------------------------------------

returns_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "North")
    & (df["product"] == "Clothing")
)

df.loc[
    returns_mask,
    "returns"
] += 10


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
    "scenario_id": "case_006",
    "scenario_type": "dominant_cause_with_red_herrings",

    "user_question": (
        "Why did overall revenue drop after 2026-08-15?"
    ),

    "target_kpi": "revenue",
    "direction": "decrease",

    "dominant_cause": "traffic_drop",
    "affected_region": "South",
    "affected_product": "Clothing",

    "incident_start": INCIDENT_START,

    "should_abstain": False,

    "expected_impact": float(expected_impact),

    "red_herrings": [
        {
            "type": "marketing_spend_drop",
            "region": "North",
            "product": "Electronics"
        },
        {
            "type": "returns_spike",
            "region": "North",
            "product": "Clothing"
        }
    ],

    "random_seed": SEED,
}


ground_truth_path = OUTPUT_DIR / "ground_truth.json"

with open(ground_truth_path, "w") as f:
    json.dump(
        ground_truth,
        f,
        indent=4
    )


print("Case 006 generated successfully.")
print(f"Dataset saved to: {data_path}")
print(f"Ground truth saved to: {ground_truth_path}")
print(f"Injected revenue impact: {expected_impact:.2f}")