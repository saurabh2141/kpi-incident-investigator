import pandas as pd

DATA_PATH = "benchmark/cases/case_008/data.csv"
INCIDENT_START = "2026-08-15"

df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])


# ---------------------------------------------------------
# 1. Overall revenue drop
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

overall_drop = ((before - after) / before) * 100

print("OVERALL KPI")
print("-----------")
print(f"Revenue BEFORE: {before:.2f}")
print(f"Revenue AFTER:  {after:.2f}")
print(f"Overall drop:   {overall_drop:.2f}%")


# ---------------------------------------------------------
# 2. True cause - South / Electronics conversion
# ---------------------------------------------------------

true_segment = df[
    (df["region"] == "South")
    & (df["product"] == "Electronics")
]

true_before = true_segment[
    true_segment["date"] < INCIDENT_START
]

true_after = true_segment[
    true_segment["date"] >= INCIDENT_START
]

conversion_before = true_before["conversion_rate"].mean()
conversion_after = true_after["conversion_rate"].mean()

revenue_before = true_before["revenue"].mean()
revenue_after = true_after["revenue"].mean()

conversion_drop = (
    (conversion_before - conversion_after)
    / conversion_before
) * 100

revenue_drop = (
    (revenue_before - revenue_after)
    / revenue_before
) * 100

print()
print("TRUE CAUSE - SOUTH / ELECTRONICS")
print("--------------------------------")
print(f"Conversion BEFORE: {conversion_before:.4f}")
print(f"Conversion AFTER:  {conversion_after:.4f}")
print(f"Conversion drop:   {conversion_drop:.2f}%")
print(f"Revenue BEFORE:    {revenue_before:.2f}")
print(f"Revenue AFTER:     {revenue_after:.2f}")
print(f"Revenue drop:      {revenue_drop:.2f}%")


# ---------------------------------------------------------
# 3. Inventory red herring
# ---------------------------------------------------------

inventory_segment = df[
    (df["region"] == "North")
    & (df["product"] == "Clothing")
]

inv_before = inventory_segment[
    inventory_segment["date"] < INCIDENT_START
]

inv_after = inventory_segment[
    inventory_segment["date"] >= INCIDENT_START
]

inventory_before = inv_before["inventory"].mean()
inventory_after = inv_after["inventory"].mean()

# Count how many rows actually became inventory constrained
stockout_rows = (
    inv_after["inventory"]
    < inv_after["orders"]
).sum()

print()
print("RED HERRING - INVENTORY")
print("-----------------------")
print(f"Inventory BEFORE: {inventory_before:.2f}")
print(f"Inventory AFTER:  {inventory_after:.2f}")
print(f"Rows where inventory < orders: {stockout_rows}")


# ---------------------------------------------------------
# 4. Marketing red herring
# ---------------------------------------------------------

marketing_segment = df[
    (df["region"] == "North")
    & (df["product"] == "Electronics")
]

marketing_before = marketing_segment[
    marketing_segment["date"] < INCIDENT_START
]["marketing_spend"].mean()

marketing_after = marketing_segment[
    marketing_segment["date"] >= INCIDENT_START
]["marketing_spend"].mean()

print()
print("RED HERRING - MARKETING")
print("-----------------------")
print(f"Marketing BEFORE: {marketing_before:.2f}")
print(f"Marketing AFTER:  {marketing_after:.2f}")