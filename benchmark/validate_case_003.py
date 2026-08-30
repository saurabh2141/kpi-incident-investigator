import pandas as pd

DATA_PATH = "benchmark/cases/case_003/data.csv"
INCIDENT_START = "2026-08-15"

df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])

# ---------------------------------------------------------
# 1. Validate overall revenue drop
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

overall_drop_pct = ((before - after) / before) * 100

print("OVERALL KPI")
print("-----------")
print(f"Average revenue BEFORE: {before:.2f}")
print(f"Average revenue AFTER:  {after:.2f}")
print(f"Overall revenue drop:   {overall_drop_pct:.2f}%")

# ---------------------------------------------------------
# 2. Validate North / Electronics revenue
# ---------------------------------------------------------

segment = df[
    (df["region"] == "North")
    & (df["product"] == "Electronics")
]

segment_before = segment[
    segment["date"] < INCIDENT_START
]

segment_after = segment[
    segment["date"] >= INCIDENT_START
]

revenue_before = segment_before["revenue"].mean()
revenue_after = segment_after["revenue"].mean()

segment_drop_pct = (
    (revenue_before - revenue_after)
    / revenue_before
) * 100

print()
print("TRUE CAUSE — NORTH / ELECTRONICS")
print("--------------------------------")
print(f"Revenue BEFORE: {revenue_before:.2f}")
print(f"Revenue AFTER:  {revenue_after:.2f}")
print(f"Revenue drop:   {segment_drop_pct:.2f}%")

# ---------------------------------------------------------
# 3. Validate conversion-rate collapse
# ---------------------------------------------------------

conversion_before = (
    segment_before["conversion_rate"].mean()
)

conversion_after = (
    segment_after["conversion_rate"].mean()
)

conversion_drop_pct = (
    (conversion_before - conversion_after)
    / conversion_before
) * 100

print()
print("CONVERSION RATE")
print("---------------")
print(f"Conversion BEFORE: {conversion_before:.4f}")
print(f"Conversion AFTER:  {conversion_after:.4f}")
print(f"Conversion drop:   {conversion_drop_pct:.2f}%")

# ---------------------------------------------------------
# 4. Check traffic stayed relatively normal
# ---------------------------------------------------------

visitors_before = segment_before["visitors"].mean()
visitors_after = segment_after["visitors"].mean()

visitor_change_pct = (
    (visitors_after - visitors_before)
    / visitors_before
) * 100

print()
print("TRAFFIC CHECK")
print("-------------")
print(f"Visitors BEFORE: {visitors_before:.2f}")
print(f"Visitors AFTER:  {visitors_after:.2f}")
print(f"Visitor change:  {visitor_change_pct:.2f}%")