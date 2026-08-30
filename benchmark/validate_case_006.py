import pandas as pd

DATA_PATH = "benchmark/cases/case_006/data.csv"
INCIDENT_START = "2026-08-15"

df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])

# ---------------------------------------------------------
# Overall revenue
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
# True cause: South / Clothing traffic
# ---------------------------------------------------------

segment = df[
    (df["region"] == "South")
    & (df["product"] == "Clothing")
]

seg_before = segment[
    segment["date"] < INCIDENT_START
]

seg_after = segment[
    segment["date"] >= INCIDENT_START
]

visitors_before = seg_before["visitors"].mean()
visitors_after = seg_after["visitors"].mean()

revenue_before = seg_before["revenue"].mean()
revenue_after = seg_after["revenue"].mean()

traffic_drop_pct = (
    (visitors_before - visitors_after)
    / visitors_before
) * 100

revenue_drop_pct = (
    (revenue_before - revenue_after)
    / revenue_before
) * 100

print()
print("TRUE CAUSE - SOUTH / CLOTHING")
print("-----------------------------")
print(f"Visitors BEFORE: {visitors_before:.2f}")
print(f"Visitors AFTER:  {visitors_after:.2f}")
print(f"Traffic drop:    {traffic_drop_pct:.2f}%")
print(f"Revenue BEFORE:  {revenue_before:.2f}")
print(f"Revenue AFTER:   {revenue_after:.2f}")
print(f"Revenue drop:    {revenue_drop_pct:.2f}%")

# ---------------------------------------------------------
# Red herring: marketing
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

# ---------------------------------------------------------
# Red herring: returns
# ---------------------------------------------------------

returns_segment = df[
    (df["region"] == "North")
    & (df["product"] == "Clothing")
]

returns_before = returns_segment[
    returns_segment["date"] < INCIDENT_START
]["returns"].mean()

returns_after = returns_segment[
    returns_segment["date"] >= INCIDENT_START
]["returns"].mean()

print()
print("RED HERRING - RETURNS")
print("---------------------")
print(f"Returns BEFORE: {returns_before:.2f}")
print(f"Returns AFTER:  {returns_after:.2f}")