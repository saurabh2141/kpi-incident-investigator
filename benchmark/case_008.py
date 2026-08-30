import json
import numpy as np
from pathlib import Path

from generate_benchmark import (
    generate_base_data,
    inject_conversion_drop,
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SEED = 336
INCIDENT_START = "2026-08-15"

OUTPUT_DIR = Path("benchmark/cases/case_008")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Generate normal business data
# ---------------------------------------------------------

df = generate_base_data(seed=SEED)


# ---------------------------------------------------------
# TRUE CAUSE
# ---------------------------------------------------------
# Conversion rate collapses for South / Electronics.
#
# This should be the actual explanation for the revenue drop.
# ---------------------------------------------------------

df, expected_impact = inject_conversion_drop(
    df=df,
    seed=337,
    region="South",
    product="Electronics",
    incident_start=INCIDENT_START,
    low=0.018,
    high=0.025,
)


# ---------------------------------------------------------
# RED HERRING 1
# ---------------------------------------------------------
# Inventory falls sharply for North / Clothing.
#
# However, inventory is deliberately kept ABOVE orders.
# Therefore it never constrains units sold and does not
# cause the revenue decline.
# ---------------------------------------------------------

inventory_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "North")
    & (df["product"] == "Clothing")
)

df.loc[
    inventory_mask,
    "inventory"
] = (
    df.loc[inventory_mask, "orders"] + 20
)

# Recalculate units sold just to prove inventory
# still does not constrain sales.

df.loc[
    inventory_mask,
    "units_sold"
] = np.minimum(
    df.loc[inventory_mask, "orders"],
    df.loc[inventory_mask, "inventory"],
)

df.loc[
    inventory_mask,
    "revenue"
] = (
    df.loc[inventory_mask, "units_sold"]
    * df.loc[inventory_mask, "price"]
)


# ---------------------------------------------------------
# RED HERRING 2
# ---------------------------------------------------------
# Marketing spend drops in North / Electronics.
#
# In this synthetic benchmark, marketing spend does not
# drive traffic, so this change should not be selected
# as the revenue mechanism.
# ---------------------------------------------------------

marketing_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "North")
    & (df["product"] == "Electronics")
)

df.loc[
    marketing_mask,
    "marketing_spend"
] *= 0.50


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
    "scenario_id": "case_008",
    "scenario_type": "dominant_cause_with_red_herrings",

    "user_question": (
        "Why did overall revenue drop after 2026-08-15?"
    ),

    "target_kpi": "revenue",
    "direction": "decrease",

    "dominant_cause": "conversion_rate_drop",
    "affected_region": "South",
    "affected_product": "Electronics",

    "incident_start": INCIDENT_START,

    "should_abstain": False,

    "expected_impact": float(expected_impact),

    "red_herrings": [
        {
            "type": "inventory_drop_without_stockout",
            "region": "North",
            "product": "Clothing",
            "reason_not_causal": (
                "Inventory remains above orders and "
                "therefore does not constrain sales."
            ),
        },
        {
            "type": "marketing_spend_drop",
            "region": "North",
            "product": "Electronics",
            "reason_not_causal": (
                "Marketing spend is not connected to "
                "visitor generation in this benchmark."
            ),
        },
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


print("Case 008 generated successfully.")
print(f"Dataset saved to: {data_path}")
print(f"Ground truth saved to: {ground_truth_path}")
print(f"Injected revenue impact: {expected_impact:.2f}")