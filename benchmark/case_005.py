import pandas as pd
import numpy as np
import json
from pathlib import Path

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SEED = 210
rng = np.random.default_rng(SEED)

OUTPUT_DIR = Path("benchmark/cases/case_005")
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

            price = 100.0 if product == "Electronics" else 60.0

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

contributors = []

# =========================================================
# Contributor 1
# North / Electronics conversion falls slightly
# =========================================================

mask_1 = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "North")
    & (df["product"] == "Electronics")
)

before_1 = df.loc[mask_1, "revenue"].copy()

df.loc[
    mask_1,
    "conversion_rate"
] *= 0.93

df.loc[
    mask_1,
    "orders"
] = (
    df.loc[mask_1, "visitors"]
    * df.loc[mask_1, "conversion_rate"]
).astype(int)

df.loc[
    mask_1,
    "units_sold"
] = np.minimum(
    df.loc[mask_1, "orders"],
    df.loc[mask_1, "inventory"],
)

df.loc[
    mask_1,
    "revenue"
] = (
    df.loc[mask_1, "units_sold"]
    * df.loc[mask_1, "price"]
)

impact_1 = (
    before_1
    - df.loc[mask_1, "revenue"]
).sum()

# =========================================================
# Contributor 2
# South / Electronics traffic falls slightly
# =========================================================

mask_2 = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "South")
    & (df["product"] == "Electronics")
)

before_2 = df.loc[mask_2, "revenue"].copy()

df.loc[
    mask_2,
    "visitors"
] = (
    df.loc[mask_2, "visitors"] * 0.94
).astype(int)

df.loc[
    mask_2,
    "orders"
] = (
    df.loc[mask_2, "visitors"]
    * df.loc[mask_2, "conversion_rate"]
).astype(int)

df.loc[
    mask_2,
    "units_sold"
] = np.minimum(
    df.loc[mask_2, "orders"],
    df.loc[mask_2, "inventory"],
)

df.loc[
    mask_2,
    "revenue"
] = (
    df.loc[mask_2, "units_sold"]
    * df.loc[mask_2, "price"]
)

impact_2 = (
    before_2
    - df.loc[mask_2, "revenue"]
).sum()

# =========================================================
# Contributor 3
# North / Clothing price falls slightly
# =========================================================

mask_3 = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "North")
    & (df["product"] == "Clothing")
)

before_3 = df.loc[mask_3, "revenue"].copy()

df.loc[
    mask_3,
    "price"
] *= 0.90

df.loc[
    mask_3,
    "revenue"
] = (
    df.loc[mask_3, "units_sold"]
    * df.loc[mask_3, "price"]
)

impact_3 = (
    before_3
    - df.loc[mask_3, "revenue"]
).sum()

# =========================================================
# Contributor 4
# South / Clothing conversion falls slightly
# =========================================================

mask_4 = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "South")
    & (df["product"] == "Clothing")
)

before_4 = df.loc[mask_4, "revenue"].copy()

df.loc[
    mask_4,
    "conversion_rate"
] *= 0.90

df.loc[
    mask_4,
    "orders"
] = (
    df.loc[mask_4, "visitors"]
    * df.loc[mask_4, "conversion_rate"]
).astype(int)

df.loc[
    mask_4,
    "units_sold"
] = np.minimum(
    df.loc[mask_4, "orders"],
    df.loc[mask_4, "inventory"],
)

df.loc[
    mask_4,
    "revenue"
] = (
    df.loc[mask_4, "units_sold"]
    * df.loc[mask_4, "price"]
)

impact_4 = (
    before_4
    - df.loc[mask_4, "revenue"]
).sum()

# ---------------------------------------------------------
# Calculate total impact
# ---------------------------------------------------------

impacts = [
    impact_1,
    impact_2,
    impact_3,
    impact_4,
]

total_expected_impact = sum(impacts)

shares = [
    impact / total_expected_impact
    for impact in impacts
]

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
    "scenario_id": "case_005",
    "scenario_type": "no_dominant_cause",
    "user_question": (
        "Why did overall revenue drop after 2026-08-15?"
    ),
    "target_kpi": "revenue",
    "direction": "decrease",

    "dominant_cause": None,
    "should_abstain": True,

    "expected_behavior": (
        "Report several small contributors but abstain "
        "from declaring one dominant root cause."
    ),

    "contributors": [
        {
            "cause": "conversion_rate_drop",
            "region": "North",
            "product": "Electronics",
            "expected_impact": float(impact_1),
            "impact_share": float(shares[0]),
        },
        {
            "cause": "traffic_drop",
            "region": "South",
            "product": "Electronics",
            "expected_impact": float(impact_2),
            "impact_share": float(shares[1]),
        },
        {
            "cause": "price_drop",
            "region": "North",
            "product": "Clothing",
            "expected_impact": float(impact_3),
            "impact_share": float(shares[2]),
        },
        {
            "cause": "conversion_rate_drop",
            "region": "South",
            "product": "Clothing",
            "expected_impact": float(impact_4),
            "impact_share": float(shares[3]),
        },
    ],

    "total_expected_impact": float(total_expected_impact),

    # No contributor should explain >= 50% of impact
    "dominance_threshold": 0.50,

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

print("Case 005 generated successfully.")
print(f"Dataset saved to: {data_path}")
print(f"Ground truth saved to: {ground_truth_path}")
print()
print(f"Contributor 1 impact: {impact_1:.2f}")
print(f"Contributor 2 impact: {impact_2:.2f}")
print(f"Contributor 3 impact: {impact_3:.2f}")
print(f"Contributor 4 impact: {impact_4:.2f}")
print(f"Total impact:         {total_expected_impact:.2f}")
print()
print(f"Contributor 1 share: {shares[0] * 100:.2f}%")
print(f"Contributor 2 share: {shares[1] * 100:.2f}%")
print(f"Contributor 3 share: {shares[2] * 100:.2f}%")
print(f"Contributor 4 share: {shares[3] * 100:.2f}%")