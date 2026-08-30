import pandas as pd

DATA_PATH = "benchmark/cases/case_002/data.csv"
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

drop_pct = ((before - after) / before) * 100

print("OVERALL KPI")
print("-----------")
print(f"Average revenue BEFORE: {before:.2f}")
print(f"Average revenue AFTER:  {after:.2f}")
print(f"Overall revenue drop:   {drop_pct:.2f}%")

# ---------------------------------------------------------
# 2. Validate true cause segment
# ---------------------------------------------------------

true_segment = df[
    (df["region"] == "South")
    & (df["product"] == "Electronics")
]

true_before = true_segment[
    true_segment["date"] < INCIDENT_START
]["revenue"].mean()

true_after = true_segment[
    true_segment["date"] >= INCIDENT_START
]["revenue"].mean()

true_drop_pct = (
    (true_before - true_after)
    / true_before
) * 100

print()
print("TRUE CAUSE — SOUTH / ELECTRONICS")
print("--------------------------------")
print(f"Revenue BEFORE: {true_before:.2f}")
print(f"Revenue AFTER:  {true_after:.2f}")
print(f"Revenue drop:   {true_drop_pct:.2f}%")

# ---------------------------------------------------------
# 3. Validate marketing red herring
# ---------------------------------------------------------

marketing_segment = df[
    (df["region"] == "North")
    & (df["product"] == "Clothing")
]

marketing_before = marketing_segment[
    marketing_segment["date"] < INCIDENT_START
]["marketing_spend"].mean()

marketing_after = marketing_segment[
    marketing_segment["date"] >= INCIDENT_START
]["marketing_spend"].mean()

marketing_change_pct = (
    (marketing_after - marketing_before)
    / marketing_before
) * 100

print()
print("RED HERRING — MARKETING")
print("-----------------------")
print(f"Marketing BEFORE: {marketing_before:.2f}")
print(f"Marketing AFTER:  {marketing_after:.2f}")
print(f"Marketing change: {marketing_change_pct:.2f}%")

# ---------------------------------------------------------
# 4. Validate returns red herring
# ---------------------------------------------------------

clothing = df[df["product"] == "Clothing"]

returns_before = clothing[
    clothing["date"] < INCIDENT_START
]["returns"].mean()

returns_after = clothing[
    clothing["date"] >= INCIDENT_START
]["returns"].mean()

print()
print("RED HERRING — RETURNS")
print("---------------------")
print(f"Returns BEFORE: {returns_before:.2f}")
print(f"Returns AFTER:  {returns_after:.2f}")