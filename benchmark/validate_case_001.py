import pandas as pd

DATA_PATH = "benchmark/cases/case_001/data.csv"

df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])

# Focus on the segment where we injected the incident
segment = df[
    (df["region"] == "South")
    & (df["product"] == "Electronics")
]

before = segment[segment["date"] < "2026-08-15"]
after = segment[segment["date"] >= "2026-08-15"]

before_avg = before["revenue"].mean()
after_avg = after["revenue"].mean()

drop_pct = ((before_avg - after_avg) / before_avg) * 100

print("CASE 001 VALIDATION")
print("-------------------")
print(f"Average revenue BEFORE incident: {before_avg:.2f}")
print(f"Average revenue AFTER incident:  {after_avg:.2f}")
print(f"Revenue drop: {drop_pct:.2f}%")

# ---------------------------------------------------------
# Validate impact on overall company revenue
# ---------------------------------------------------------

daily_revenue = (
    df.groupby("date")["revenue"]
    .sum()
    .reset_index()
)

overall_before = daily_revenue[
    daily_revenue["date"] < "2026-08-15"
]["revenue"].mean()

overall_after = daily_revenue[
    daily_revenue["date"] >= "2026-08-15"
]["revenue"].mean()

overall_drop_pct = (
    (overall_before - overall_after)
    / overall_before
) * 100

print()
print("OVERALL KPI VALIDATION")
print("----------------------")
print(f"Average daily revenue BEFORE: {overall_before:.2f}")
print(f"Average daily revenue AFTER:  {overall_after:.2f}")
print(f"Overall revenue drop: {overall_drop_pct:.2f}%")