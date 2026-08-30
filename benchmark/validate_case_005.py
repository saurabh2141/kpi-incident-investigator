import pandas as pd

DATA_PATH = "benchmark/cases/case_005/data.csv"
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
# 2. Validate each segment changed only moderately
# ---------------------------------------------------------

segments = [
    ("North", "Electronics"),
    ("South", "Electronics"),
    ("North", "Clothing"),
    ("South", "Clothing"),
]

print()
print("SEGMENT REVENUE CHANGES")
print("-----------------------")

for region, product in segments:

    segment = df[
        (df["region"] == region)
        & (df["product"] == product)
    ]

    seg_before = segment[
        segment["date"] < INCIDENT_START
    ]["revenue"].mean()

    seg_after = segment[
        segment["date"] >= INCIDENT_START
    ]["revenue"].mean()

    change_pct = (
        (seg_after - seg_before)
        / seg_before
    ) * 100

    print(
        f"{region} / {product}: "
        f"{change_pct:.2f}%"
    )