import json
from pathlib import Path

from generate_benchmark import (
    generate_base_data,
    inject_traffic_drop,
    inject_price_drop,
)


SEED = 378
INCIDENT_START = "2026-08-15"

OUTPUT_DIR = Path("benchmark/cases/case_009")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Generate normal business data
# ---------------------------------------------------------

df = generate_base_data(seed=SEED)


# ---------------------------------------------------------
# Contributor 1: Traffic drop
# North / Electronics
# ---------------------------------------------------------

df, traffic_impact = inject_traffic_drop(
    df=df,
    region="North",
    product="Electronics",
    incident_start=INCIDENT_START,
    multiplier=0.72,
)


# ---------------------------------------------------------
# Contributor 2: Price drop
# South / Clothing
# ---------------------------------------------------------

df, price_impact = inject_price_drop(
    df=df,
    region="South",
    product="Clothing",
    incident_start=INCIDENT_START,
    multiplier=0.55,
)


# ---------------------------------------------------------
# Calculate combined impact
# ---------------------------------------------------------

total_expected_impact = traffic_impact + price_impact

traffic_share = traffic_impact / total_expected_impact
price_share = price_impact / total_expected_impact


# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

data_path = OUTPUT_DIR / "data.csv"
df.to_csv(data_path, index=False)


# ---------------------------------------------------------
# Save ground truth
# ---------------------------------------------------------

ground_truth = {
    "scenario_id": "case_009",
    "scenario_type": "multiple_contributing_causes",

    "user_question": (
        "Why did overall revenue drop after 2026-08-15?"
    ),

    "target_kpi": "revenue",
    "direction": "decrease",

    "dominant_cause": None,
    "should_abstain": True,

    "expected_behavior": (
        "Report multiple material contributors and abstain "
        "from declaring one dominant root cause."
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
            "product": "Clothing",
            "expected_impact": float(price_impact),
            "impact_share": float(price_share),
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


print("Case 009 generated successfully.")
print(f"Dataset saved to: {data_path}")
print(f"Ground truth saved to: {ground_truth_path}")
print()
print(f"Traffic impact: {traffic_impact:.2f}")
print(f"Price impact:   {price_impact:.2f}")
print(f"Combined impact: {total_expected_impact:.2f}")
print()
print(f"Traffic share: {traffic_share * 100:.2f}%")
print(f"Price share:   {price_share * 100:.2f}%")