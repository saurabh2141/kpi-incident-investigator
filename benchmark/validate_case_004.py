import pandas as pd

DATA_PATH = "benchmark/cases/case_004/data.csv"
INCIDENT_START = "2026-08-15"

df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])

# ---------------------------------------------------------
# 1. Overall revenue change
# ---------------------------------------------------------

daily_revenue = (
    df.groupby("date")["revenue"]
    .sum()
    .reset_index()
)

before = daily_revenue[
    daily_revenue["date"] < INCIDENT_START
]["revenue"].mean()

after = daily_revenue[
    daily_revenue["date"] >= INCIDENT_START
]["revenue"].mean()

drop_pct = ((before - after) / before) * 100

print("OVERALL KPI")
print("-----------")
print(f"Revenue BEFORE: {before:.2f}")
print(f"Revenue AFTER:  {after:.2f}")
print(f"Overall drop:   {drop_pct:.2f}%")

# ---------------------------------------------------------
# 2. Contributor 1 - North / Electronics conversion
# ---------------------------------------------------------

north_electronics = df[
    (df["region"] == "North")
    & (df["product"] == "Electronics")
]

ne_before = north_electronics[
    north_electronics["date"] < INCIDENT_START
]

ne_after = north_electronics[
    north_electronics["date"] >= INCIDENT_START
]

conversion_before = ne_before["conversion_rate"].mean()
conversion_after = ne_after["conversion_rate"].mean()

revenue_before = ne_before["revenue"].mean()
revenue_after = ne_after["revenue"].mean()

print()
print("CONTRIBUTOR 1 - CONVERSION")
print("--------------------------")
print(f"Conversion BEFORE: {conversion_before:.4f}")
print(f"Conversion AFTER:  {conversion_after:.4f}")
print(f"Revenue BEFORE:    {revenue_before:.2f}")
print(f"Revenue AFTER:     {revenue_after:.2f}")

# ---------------------------------------------------------
# 3. Contributor 2 - South / Clothing inventory
# ---------------------------------------------------------

south_clothing = df[
    (df["region"] == "South")
    & (df["product"] == "Clothing")
]

sc_before = south_clothing[
    south_clothing["date"] < INCIDENT_START
]

sc_after = south_clothing[
    south_clothing["date"] >= INCIDENT_START
]

inventory_before = sc_before["inventory"].mean()
inventory_after = sc_after["inventory"].mean()

revenue_before_2 = sc_before["revenue"].mean()
revenue_after_2 = sc_after["revenue"].mean()

print()
print("CONTRIBUTOR 2 - INVENTORY")
print("-------------------------")
print(f"Inventory BEFORE: {inventory_before:.2f}")
print(f"Inventory AFTER:  {inventory_after:.2f}")
print(f"Revenue BEFORE:   {revenue_before_2:.2f}")
print(f"Revenue AFTER:    {revenue_after_2:.2f}")