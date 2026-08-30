import pandas as pd

DATA_PATH = "benchmark/cases/case_011/data.csv"
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
# 2. Check South / Clothing inventory red herring
# ---------------------------------------------------------

segment = df[
    (df["region"] == "South")
    & (df["product"] == "Clothing")
]

after_segment = segment[
    segment["date"] >= INCIDENT_START
]

stockout_rows = (
    after_segment["inventory"]
    < after_segment["orders"]
).sum()

print()
print("INVENTORY RED HERRING")
print("---------------------")
print(
    f"Rows where inventory < orders: "
    f"{stockout_rows}"
)


# ---------------------------------------------------------
# 3. Marketing red herring
# ---------------------------------------------------------

marketing_before = segment[
    segment["date"] < INCIDENT_START
]["marketing_spend"].mean()

marketing_after = segment[
    segment["date"] >= INCIDENT_START
]["marketing_spend"].mean()

marketing_drop = (
    (marketing_before - marketing_after)
    / marketing_before
) * 100

print()
print("MARKETING RED HERRING")
print("---------------------")
print(f"Marketing BEFORE: {marketing_before:.2f}")
print(f"Marketing AFTER:  {marketing_after:.2f}")
print(f"Marketing drop:   {marketing_drop:.2f}%")


# ---------------------------------------------------------
# 4. Validate actual contributors
# ---------------------------------------------------------

contributors = [
    ("North", "Electronics"),
    ("South", "Electronics"),
    ("North", "Clothing"),
]

print()
print("CONTRIBUTOR REVENUE CHANGES")
print("---------------------------")

for region, product in contributors:

    current = df[
        (df["region"] == region)
        & (df["product"] == product)
    ]

    seg_before = current[
        current["date"] < INCIDENT_START
    ]["revenue"].mean()

    seg_after = current[
        current["date"] >= INCIDENT_START
    ]["revenue"].mean()

    change = (
        (seg_after - seg_before)
        / seg_before
    ) * 100

    print(
        f"{region} / {product}: "
        f"{change:.2f}%"
    )