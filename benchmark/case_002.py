import pandas as pd
import numpy as np
import json
from pathlib import Path

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SEED = 84
rng = np.random.default_rng(SEED)

OUTPUT_DIR = Path("benchmark/cases/case_002")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INCIDENT_START = pd.Timestamp("2026-08-15")

# ---------------------------------------------------------
# Create normal business data
# ---------------------------------------------------------

dates = pd.date_range("2026-07-01", "2026-08-31", freq="D")
regions = ["North", "South"]
products = ["Electronics", "Clothing"]

rows = []

for date in dates:
    for region in regions:
        for product in products:

            visitors = int(rng.integers(800, 1200))

            conversion_rate = rng.uniform(0.04, 0.06)
            orders = int(visitors * conversion_rate)

            price = 100 if product == "Electronics" else 60

            inventory = int(rng.integers(80, 130))

            units_sold = min(orders, inventory)

            revenue = units_sold * price

            marketing_spend = float(
                rng.integers(800, 1200)
            )

            returns = int(
                rng.integers(1, 5)
            )

            rows.append(
                {
                    "date": date,
                    "region": region,
                    "product": product,
                    "visitors": visitors,
                    "orders": orders,
                    "inventory": inventory,
                    "units_sold": units_sold,
                    "price": price,
                    "marketing_spend": marketing_spend,
                    "returns": returns,
                    "revenue": revenue,
                }
            )

df = pd.DataFrame(rows)

# ---------------------------------------------------------
# TRUE INCIDENT
# ---------------------------------------------------------
# True cause:
# Electronics inventory in South collapses after Aug 15.
#
# This is the actual cause of the revenue decline.
# ---------------------------------------------------------

true_cause_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "South")
    & (df["product"] == "Electronics")
)

# Save counterfactual revenue before injecting the incident
counterfactual_revenue = df.loc[
    true_cause_mask, "revenue"
].copy()

# Collapse inventory
df.loc[
    true_cause_mask, "inventory"
] = rng.integers(
    5,
    15,
    size=true_cause_mask.sum()
)

# Recalculate downstream values
df.loc[
    true_cause_mask, "units_sold"
] = np.minimum(
    df.loc[true_cause_mask, "orders"],
    df.loc[true_cause_mask, "inventory"],
)

df.loc[
    true_cause_mask, "revenue"
] = (
    df.loc[true_cause_mask, "units_sold"]
    * df.loc[true_cause_mask, "price"]
)

# Exact revenue loss caused by true incident
expected_impact = (
    counterfactual_revenue
    - df.loc[true_cause_mask, "revenue"]
).sum()

# ---------------------------------------------------------
# RED HERRING 1
# ---------------------------------------------------------
# Marketing spend suddenly decreases in North/Clothing.
#
# Important:
# Marketing spend does NOT drive visitors in this synthetic
# dataset, so this change is correlated in time but is not
# responsible for the revenue incident.
# ---------------------------------------------------------

marketing_red_herring_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "North")
    & (df["product"] == "Clothing")
)

df.loc[
    marketing_red_herring_mask,
    "marketing_spend",
] *= 0.60

# ---------------------------------------------------------
# RED HERRING 2
# ---------------------------------------------------------
# Returns increase for Clothing after Aug 15.
#
# Revenue here represents gross sales revenue.
# Therefore this returns spike is intentionally not the
# mechanism causing the observed gross-revenue decline.
# ---------------------------------------------------------

returns_red_herring_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["product"] == "Clothing")
)

df.loc[
    returns_red_herring_mask,
    "returns",
] += 8

# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

data_path = OUTPUT_DIR / "data.csv"
df.to_csv(data_path, index=False)

# ---------------------------------------------------------
# Save ground truth
# ---------------------------------------------------------

ground_truth = {
    "scenario_id": "case_002",
    "scenario_type": "dominant_cause_with_red_herrings",
    "user_question": (
        "Why did overall revenue drop after 2026-08-15?"
    ),
    "target_kpi": "revenue",
    "direction": "decrease",
    "dominant_cause": "inventory_shortage",
    "affected_region": "South",
    "affected_product": "Electronics",
    "incident_start": "2026-08-15",
    "should_abstain": False,
    "expected_impact": float(expected_impact),
    "red_herrings": [
        {
            "type": "marketing_spend_drop",
            "region": "North",
            "product": "Clothing"
        },
        {
            "type": "returns_spike",
            "region": "All",
            "product": "Clothing"
        }
    ],
    "random_seed": SEED,
}

ground_truth_path = OUTPUT_DIR / "ground_truth.json"

with open(ground_truth_path, "w") as f:
    json.dump(ground_truth, f, indent=4)

print("Case 002 generated successfully.")
print(f"Dataset saved to: {data_path}")
print(f"Ground truth saved to: {ground_truth_path}")
print(f"Injected revenue impact: {expected_impact:.2f}")