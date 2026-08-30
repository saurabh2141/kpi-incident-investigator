import pandas as pd

DATA_PATH = "benchmark/cases/case_009/data.csv"
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
# 2. Contributor 1 - North / Electronics traffic
# ---------------------------------------------------------

segment_1 = df[
    (df["region"] == "North")
    & (df["product"] == "Electronics")
]

before_1 = segment_1[
    segment_1["date"] < INCIDENT_START
]

after_1 = segment_1[
    segment_1["date"] >= INCIDENT_START
]

visitors_before = before_1["visitors"].mean()
visitors_after = after_1["visitors"].mean()

revenue_before_1 = before_1["revenue"].mean()
revenue_after_1 = after_1["revenue"].mean()

print()
print("CONTRIBUTOR 1 - TRAFFIC")
print("-----------------------")
print(f"Visitors BEFORE: {visitors_before:.2f}")
print(f"Visitors AFTER:  {visitors_after:.2f}")
print(f"Revenue BEFORE:  {revenue_before_1:.2f}")
print(f"Revenue AFTER:   {revenue_after_1:.2f}")

# ---------------------------------------------------------
# 3. Contributor 2 - South / Clothing price
# ---------------------------------------------------------

segment_2 = df[
    (df["region"] == "South")
    & (df["product"] == "Clothing")
]

before_2 = segment_2[
    segment_2["date"] < INCIDENT_START
]

after_2 = segment_2[
    segment_2["date"] >= INCIDENT_START
]

price_before = before_2["price"].mean()
price_after = after_2["price"].mean()

revenue_before_2 = before_2["revenue"].mean()
revenue_after_2 = after_2["revenue"].mean()

print()
print("CONTRIBUTOR 2 - PRICE")
print("---------------------")
print(f"Price BEFORE:   {price_before:.2f}")
print(f"Price AFTER:    {price_after:.2f}")
print(f"Revenue BEFORE: {revenue_before_2:.2f}")
print(f"Revenue AFTER:  {revenue_after_2:.2f}")