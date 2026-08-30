import pandas as pd

DATA_PATH = "benchmark/cases/case_007/data.csv"
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
# 2. South / Electronics segment
# ---------------------------------------------------------

segment = df[
    (df["region"] == "South")
    & (df["product"] == "Electronics")
]

seg_before = segment[
    segment["date"] < INCIDENT_START
]

seg_after = segment[
    segment["date"] >= INCIDENT_START
]

price_before = seg_before["price"].mean()
price_after = seg_after["price"].mean()

revenue_before = seg_before["revenue"].mean()
revenue_after = seg_after["revenue"].mean()

print()
print("TRUE CAUSE - SOUTH / ELECTRONICS")
print("--------------------------------")
print(f"Price BEFORE:   {price_before:.2f}")
print(f"Price AFTER:    {price_after:.2f}")
print(f"Revenue BEFORE: {revenue_before:.2f}")
print(f"Revenue AFTER:  {revenue_after:.2f}")

# ---------------------------------------------------------
# 3. Check traffic stayed normal
# ---------------------------------------------------------

visitors_before = seg_before["visitors"].mean()
visitors_after = seg_after["visitors"].mean()

visitor_change = (
    (visitors_after - visitors_before)
    / visitors_before
) * 100

print()
print("TRAFFIC CHECK")
print("-------------")
print(f"Visitors BEFORE: {visitors_before:.2f}")
print(f"Visitors AFTER:  {visitors_after:.2f}")
print(f"Visitor change:  {visitor_change:.2f}%")

# ---------------------------------------------------------
# 4. Check conversion stayed normal
# ---------------------------------------------------------

conversion_before = seg_before["conversion_rate"].mean()
conversion_after = seg_after["conversion_rate"].mean()

conversion_change = (
    (conversion_after - conversion_before)
    / conversion_before
) * 100

print()
print("CONVERSION CHECK")
print("----------------")
print(f"Conversion BEFORE: {conversion_before:.4f}")
print(f"Conversion AFTER:  {conversion_after:.4f}")
print(f"Conversion change: {conversion_change:.2f}%")

# ---------------------------------------------------------
# 5. Check inventory stayed normal
# ---------------------------------------------------------

inventory_before = seg_before["inventory"].mean()
inventory_after = seg_after["inventory"].mean()

inventory_change = (
    (inventory_after - inventory_before)
    / inventory_before
) * 100

print()
print("INVENTORY CHECK")
print("---------------")
print(f"Inventory BEFORE: {inventory_before:.2f}")
print(f"Inventory AFTER:  {inventory_after:.2f}")
print(f"Inventory change: {inventory_change:.2f}%")