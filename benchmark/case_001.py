import pandas as pd
import numpy as np
import json
from pathlib import Path

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SEED = 42
np.random.seed(SEED)

OUTPUT_DIR = Path("benchmark/cases/case_001")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

            visitors = np.random.randint(800, 1200)

            conversion_rate = np.random.uniform(0.04, 0.06)
            orders = int(visitors * conversion_rate)

            price = 100 if product == "Electronics" else 60

            inventory = np.random.randint(80, 130)

            units_sold = min(orders, inventory)

            revenue = units_sold * price

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
                    "revenue": revenue,
                }
            )

df = pd.DataFrame(rows)

# ---------------------------------------------------------
# Inject known incident
# ---------------------------------------------------------
# Ground truth:
# Electronics inventory in the South region collapses
# from Aug 15 onward, causing revenue to fall.

incident_mask = (
    (df["date"] >= "2026-08-15")
    & (df["region"] == "South")
    & (df["product"] == "Electronics")
)

# Save the revenue that would have occurred without the incident
counterfactual_revenue = df.loc[incident_mask, "revenue"].copy()

df.loc[incident_mask, "inventory"] = np.random.randint(
    5, 15, size=incident_mask.sum()
)

# Recalculate downstream values after inventory shortage

df.loc[incident_mask, "units_sold"] = np.minimum(
    df.loc[incident_mask, "orders"],
    df.loc[incident_mask, "inventory"],
)

df.loc[incident_mask, "revenue"] = (
    df.loc[incident_mask, "units_sold"]
    * df.loc[incident_mask, "price"]
)

# Calculate the exact revenue loss caused by our injected incident
expected_impact = (
    counterfactual_revenue
    - df.loc[incident_mask, "revenue"]
).sum()

# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

data_path = OUTPUT_DIR / "data.csv"
df.to_csv(data_path, index=False)

# ---------------------------------------------------------
# Save ground truth
# ---------------------------------------------------------

ground_truth = {
    "scenario_id": "case_001",
    "scenario_type": "single_dominant_cause",
    "target_kpi": "revenue",
    "direction": "decrease",
    "dominant_cause": "inventory_shortage",
    "affected_region": "South",
    "affected_product": "Electronics",
    "incident_start": "2026-08-15",
    "should_abstain": False,
    "expected_impact": float(expected_impact),
    "random_seed": SEED,
}

ground_truth_path = OUTPUT_DIR / "ground_truth.json"

with open(ground_truth_path, "w") as f:
    json.dump(ground_truth, f, indent=4)

print("Case 001 generated successfully.")
print(f"Dataset saved to: {data_path}")
print(f"Ground truth saved to: {ground_truth_path}")