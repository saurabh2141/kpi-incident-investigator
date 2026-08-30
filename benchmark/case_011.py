import json
import numpy as np
from pathlib import Path

from generate_benchmark import (
    generate_base_data,
    inject_traffic_drop,
    inject_price_drop,
    inject_conversion_drop,
)


SEED = 462
INCIDENT_START = "2026-08-15"

OUTPUT_DIR = Path("benchmark/cases/case_011")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Generate normal business data
# ---------------------------------------------------------

df = generate_base_data(seed=SEED)


# ---------------------------------------------------------
# Small contributor 1:
# North / Electronics traffic decreases moderately
# ---------------------------------------------------------

df, traffic_impact = inject_traffic_drop(
    df=df,
    region="North",
    product="Electronics",
    incident_start=INCIDENT_START,
    multiplier=0.90,
)


# ---------------------------------------------------------
# Small contributor 2:
# South / Electronics price decreases moderately
# ---------------------------------------------------------

df, price_impact = inject_price_drop(
    df=df,
    region="South",
    product="Electronics",
    incident_start=INCIDENT_START,
    multiplier=0.90,
)


# ---------------------------------------------------------
# Small contributor 3:
# North / Clothing conversion decreases moderately
# ---------------------------------------------------------

df, conversion_impact = inject_conversion_drop(
    df=df,
    seed=463,
    region="North",
    product="Clothing",
    incident_start=INCIDENT_START,
    low=0.040,
    high=0.045,
)


# ---------------------------------------------------------
# RED HERRING 1
# Marketing spend collapses in South / Clothing.
#
# Marketing does not mechanically control visitors in
# this synthetic benchmark.
# ---------------------------------------------------------

marketing_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "South")
    & (df["product"] == "Clothing")
)

df.loc[
    marketing_mask,
    "marketing_spend"
] *= 0.40


# ---------------------------------------------------------
# RED HERRING 2
# Inventory falls substantially in South / Clothing,
# but remains above orders and therefore never limits sales.
# ---------------------------------------------------------

inventory_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "South")
    & (df["product"] == "Clothing")
)

df.loc[
    inventory_mask,
    "inventory"
] = (
    df.loc[inventory_mask, "orders"] + 15
)

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
# Calculate contribution shares
# ---------------------------------------------------------

total_expected_impact = (
    traffic_impact
    + price_impact
    + conversion_impact
)

traffic_share = traffic_impact / total_expected_impact
price_share = price_impact / total_expected_impact
conversion_share = conversion_impact / total_expected_impact


# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

data_path = OUTPUT_DIR / "data.csv"
df.to_csv(data_path, index=False)


# ---------------------------------------------------------
# Save ground truth
# ---------------------------------------------------------

ground_truth = {
    "scenario_id": "case_011",
    "scenario_type": "no_dominant_cause_with_red_herrings",

    "user_question": (
        "Why did overall revenue drop after 2026-08-15?"
    ),

    "target_kpi": "revenue",
    "direction": "decrease",

    "dominant_cause": None,
    "should_abstain": True,

    "expected_behavior": (
        "Identify several modest contributors, reject the "
        "non-causal red herrings, and abstain from declaring "
        "one dominant root cause."
    ),

    "contributors": [
        {
            "cause": "traffic_drop",
            "region": "North",
            "product": "Electronics",
            "expected_impact": float(traffic_impact),
            "impact_share": float(traffic_share),
        },
        {
            "cause": "price_drop",
            "region": "South",
            "product": "Electronics",
            "expected_impact": float(price_impact),
            "impact_share": float(price_share),
        },
        {
            "cause": "conversion_rate_drop",
            "region": "North",
            "product": "Clothing",
            "expected_impact": float(conversion_impact),
            "impact_share": float(conversion_share),
        },
    ],

    "red_herrings": [
        {
            "type": "marketing_spend_drop",
            "region": "South",
            "product": "Clothing",
        },
        {
            "type": "inventory_drop_without_stockout",
            "region": "South",
            "product": "Clothing",
        },
    ],

    "total_expected_impact": float(total_expected_impact),
    "dominance_threshold": 0.50,
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


print("Case 011 generated successfully.")
print(f"Dataset saved to: {data_path}")
print(f"Ground truth saved to: {ground_truth_path}")
print()
print(f"Traffic impact:    {traffic_impact:.2f}")
print(f"Price impact:      {price_impact:.2f}")
print(f"Conversion impact: {conversion_impact:.2f}")
print(f"Total impact:      {total_expected_impact:.2f}")
print()
print(f"Traffic share:    {traffic_share * 100:.2f}%")
print(f"Price share:      {price_share * 100:.2f}%")
print(f"Conversion share: {conversion_share * 100:.2f}%")