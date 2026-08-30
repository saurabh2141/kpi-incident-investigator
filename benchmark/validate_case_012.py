import pandas as pd

DATA_PATH = "benchmark/cases/case_012/data.csv"
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

change_pct = (
    (after - before)
    / before
) * 100

print("OVERALL KPI")
print("-----------")
print(f"Revenue BEFORE: {before:.2f}")
print(f"Revenue AFTER:  {after:.2f}")
print(f"Revenue change: {change_pct:.2f}%")

# ---------------------------------------------------------
# 2. Marketing red herring
# ---------------------------------------------------------

segment = df[
    (df["region"] == "North")
    & (df["product"] == "Electronics")
]

marketing_before = segment[
    segment["date"] < INCIDENT_START
]["marketing_spend"].mean()

marketing_after = segment[
    segment["date"] >= INCIDENT_START
]["marketing_spend"].mean()

marketing_change = (
    (marketing_after - marketing_before)
    / marketing_before
) * 100

print()
print("MARKETING RED HERRING")
print("---------------------")
print(f"Marketing BEFORE: {marketing_before:.2f}")
print(f"Marketing AFTER:  {marketing_after:.2f}")
print(f"Marketing change: {marketing_change:.2f}%")

# ---------------------------------------------------------
# 3. Check revenue by segment
# ---------------------------------------------------------

segments = [
    ("North", "Electronics"),
    ("South", "Electronics"),
    ("North", "Clothing"),
    ("South", "Clothing"),
]

print()
print("SEGMENT DRIVER CHECK")
print("--------------------")

for region, product in segments:

    current = df[
        (df["region"] == region)
        & (df["product"] == product)
    ]

    before_rows = current[
        current["date"] < INCIDENT_START
    ]

    after_rows = current[
        current["date"] >= INCIDENT_START
    ]

    visitors_before = before_rows["visitors"].mean()
    visitors_after = after_rows["visitors"].mean()

    conversion_before = before_rows["conversion_rate"].mean()
    conversion_after = after_rows["conversion_rate"].mean()

    visitor_change = (
        (visitors_after - visitors_before)
        / visitors_before
    ) * 100

    conversion_change = (
        (conversion_after - conversion_before)
        / conversion_before
    ) * 100

    print()
    print(f"{region} / {product}")
    print(f"Visitor change:    {visitor_change:.2f}%")
    print(f"Conversion change: {conversion_change:.2f}%")