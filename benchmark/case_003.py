import pandas as pd
import numpy as np
import json
from pathlib import Path

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SEED = 126
rng = np.random.default_rng(SEED)

OUTPUT_DIR = Path("benchmark/cases/case_003")
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

# ---------------------------------------------------------
# Inject known incident
# ---------------------------------------------------------
# True cause:
#
# Conversion rate for Electronics in the North region
# collapses after Aug 15.
#
# Traffic remains normal.
# Inventory remains normal.
#
# Therefore the revenue decline is caused specifically
# by weaker conversion.
# ---------------------------------------------------------

incident_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "North")
    & (df["product"] == "Electronics")
)

# Save what revenue would have been without the incident
counterfactual_revenue = df.loc[
    incident_mask,
    "revenue"
].copy()

# Collapse conversion rate
df.loc[
    incident_mask,
    "conversion_rate"
] = rng.uniform(
    0.01,
    0.02,
    size=incident_mask.sum()
)

# Recalculate orders
df.loc[
    incident_mask,
    "orders"
] = (
    df.loc[incident_mask, "visitors"]
    * df.loc[incident_mask, "conversion_rate"]
).astype(int)

# Recalculate units sold
df.loc[
    incident_mask,
    "units_sold"
] = np.minimum(
    df.loc[incident_mask, "orders"],
    df.loc[incident_mask, "inventory"],
)

# Recalculate revenue
df.loc[
    incident_mask,
    "revenue"
] = (
    df.loc[incident_mask, "units_sold"]
    * df.loc[incident_mask, "price"]
)

# ---------------------------------------------------------
# Calculate exact injected impact
# ---------------------------------------------------------

expected_impact = (
    counterfactual_revenue
    - df.loc[incident_mask, "revenue"]
).sum()

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
    "scenario_id": "case_003",
    "scenario_type": "single_dominant_cause",
    "user_question": (
        "Why did overall revenue drop after 2026-08-15?"
    ),
    "target_kpi": "revenue",
    "direction": "decrease",
    "dominant_cause": "conversion_rate_drop",
    "affected_region": "North",
    "affected_product": "Electronics",
    "incident_start": "2026-08-15",
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

print("Case 003 generated successfully.")
print(f"Dataset saved to: {data_path}")
print(f"Ground truth saved to: {ground_truth_path}")
print(f"Injected revenue impact: {expected_impact:.2f}")