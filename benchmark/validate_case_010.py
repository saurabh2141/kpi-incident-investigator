import pandas as pd

DATA_PATH = "benchmark/cases/case_010/data.csv"
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
# 2. Contributor 1 - South / Electronics inventory
# ---------------------------------------------------------

segment_1 = df[
    (df["region"] == "South")
    & (df["product"] == "Electronics")
]

before_1 = segment_1[
    segment_1["date"] < INCIDENT_START
]

after_1 = segment_1[
    segment_1["date"] >= INCIDENT_START
]

inventory_before = before_1["inventory"].mean()
inventory_after = after_1["inventory"].mean()

revenue_before_1 = before_1["revenue"].mean()
revenue_after_1 = after_1["revenue"].mean()

print()
print("CONTRIBUTOR 1 - INVENTORY")
print("-------------------------")
print(f"Inventory BEFORE: {inventory_before:.2f}")
print(f"Inventory AFTER:  {inventory_after:.2f}")
print(f"Revenue BEFORE:   {revenue_before_1:.2f}")
print(f"Revenue AFTER:    {revenue_after_1:.2f}")

# ---------------------------------------------------------
# 3. Contributor 2 - North / Clothing conversion
# ---------------------------------------------------------

segment_2 = df[
    (df["region"] == "North")
    & (df["product"] == "Clothing")
]

before_2 = segment_2[
    segment_2["date"] < INCIDENT_START
]

after_2 = segment_2[
    segment_2["date"] >= INCIDENT_START
]

conversion_before = before_2["conversion_rate"].mean()
conversion_after = after_2["conversion_rate"].mean()

revenue_before_2 = before_2["revenue"].mean()
revenue_after_2 = after_2["revenue"].mean()

print()
print("CONTRIBUTOR 2 - CONVERSION")
print("--------------------------")
print(f"Conversion BEFORE: {conversion_before:.4f}")
print(f"Conversion AFTER:  {conversion_after:.4f}")
print(f"Revenue BEFORE:    {revenue_before_2:.2f}")
print(f"Revenue AFTER:     {revenue_after_2:.2f}")