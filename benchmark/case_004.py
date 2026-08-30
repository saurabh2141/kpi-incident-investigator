import pandas as pd
import numpy as np
import json
from pathlib import Path

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SEED = 168
rng = np.random.default_rng(SEED)

OUTPUT_DIR = Path("benchmark/cases/case_004")
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

            conversion_rate = float(
                rng.uniform(0.04, 0.06)
            )

            orders = int(
                visitors * conversion_rate
            )

            price = 100 if product == "Electronics" else 60

            inventory = int(
                rng.integers(100, 150)
            )

            units_sold = min(
                orders,
                inventory
            )

            revenue = units_sold * price

            rows.append(
                {
                    "date": date,
                    "region": region,
                    "product": product,
                    "visitors": visitors,
                    "conversion_rate": conversion_rate,
                    "orders": orders,
                    "inventory": inventory,
                    "units_sold": units_sold,
                    "price": price,
                    "revenue": revenue,
                }
            )

df = pd.DataFrame(rows)

# =========================================================
# CONTRIBUTOR 1
# North / Electronics conversion-rate decline
# =========================================================

conversion_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "North")
    & (df["product"] == "Electronics")
)

conversion_counterfactual = df.loc[
    conversion_mask,
    "revenue"
].copy()

# Reduce conversion, but not catastrophically
df.loc[
    conversion_mask,
    "conversion_rate"
] = rng.uniform(
    0.030,
    0.035,
    size=conversion_mask.sum()
)

df.loc[
    conversion_mask,
    "orders"
] = (
    df.loc[conversion_mask, "visitors"]
    * df.loc[conversion_mask, "conversion_rate"]
).astype(int)

df.loc[
    conversion_mask,
    "units_sold"
] = np.minimum(
    df.loc[conversion_mask, "orders"],
    df.loc[conversion_mask, "inventory"],
)

df.loc[
    conversion_mask,
    "revenue"
] = (
    df.loc[conversion_mask, "units_sold"]
    * df.loc[conversion_mask, "price"]
)

conversion_impact = (
    conversion_counterfactual
    - df.loc[conversion_mask, "revenue"]
).sum()

# =========================================================
# CONTRIBUTOR 2
# South / Clothing inventory shortage
# =========================================================

inventory_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "South")
    & (df["product"] == "Clothing")
)

inventory_counterfactual = df.loc[
    inventory_mask,
    "revenue"
].copy()

# Reduce inventory enough to constrain sales
df.loc[
    inventory_mask,
    "inventory"
] = rng.integers(
    18,
    28,
    size=inventory_mask.sum()
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

inventory_impact = (
    inventory_counterfactual
    - df.loc[inventory_mask, "revenue"]
).sum()

# ---------------------------------------------------------
# Calculate combined impact
# ---------------------------------------------------------

total_expected_impact = (
    conversion_impact
    + inventory_impact
)

conversion_share = (
    conversion_impact
    / total_expected_impact
)

inventory_share = (
    inventory_impact
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
    "scenario_id": "case_004",
    "scenario_type": "multiple_contributing_causes",
    "user_question": (
        "Why did overall revenue drop after 2026-08-15?"
    ),
    "target_kpi": "revenue",
    "direction": "decrease",

    # No single dominant cause should be claimed
    "dominant_cause": None,
    "should_abstain": True,

    "expected_behavior": (
        "Report multiple material contributors and abstain "
        "from declaring one dominant root cause."
    ),

    "contributors": [
        {
            "cause": "conversion_rate_drop",
            "region": "North",
            "product": "Electronics",
            "expected_impact": float(conversion_impact),
            "impact_share": float(conversion_share),
        },
        {
            "cause": "inventory_shortage",
            "region": "South",
            "product": "Clothing",
            "expected_impact": float(inventory_impact),
            "impact_share": float(inventory_share),
        }
    ],

    "total_expected_impact": float(total_expected_impact),
    "incident_start": "2026-08-15",
    "random_seed": SEED,
}

ground_truth_path = OUTPUT_DIR / "ground_truth.json"

with open(ground_truth_path, "w") as f:
    json.dump(
        ground_truth,
        f,
        indent=4
    )

print("Case 004 generated successfully.")
print(f"Dataset saved to: {data_path}")
print(f"Ground truth saved to: {ground_truth_path}")
print()
print(f"Conversion impact: {conversion_impact:.2f}")
print(f"Inventory impact:  {inventory_impact:.2f}")
print(f"Combined impact:   {total_expected_impact:.2f}")
print()
print(f"Conversion share: {conversion_share * 100:.2f}%")
print(f"Inventory share:  {inventory_share * 100:.2f}%")