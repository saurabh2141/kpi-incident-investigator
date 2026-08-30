import pandas as pd
import numpy as np
from pathlib import Path


# ---------------------------------------------------------
# Shared configuration
# ---------------------------------------------------------

START_DATE = "2026-07-01"
END_DATE = "2026-08-31"

REGIONS = ["North", "South"]
PRODUCTS = ["Electronics", "Clothing"]


# ---------------------------------------------------------
# Generate normal business data
# ---------------------------------------------------------

def generate_base_data(seed: int) -> pd.DataFrame:
    """
    Create deterministic synthetic business data.

    No incident is injected here.
    This function only creates the normal baseline business.
    """

    rng = np.random.default_rng(seed)

    dates = pd.date_range(
        START_DATE,
        END_DATE,
        freq="D"
    )

    rows = []

    for date in dates:
        for region in REGIONS:
            for product in PRODUCTS:

                visitors = int(
                    rng.integers(800, 1200)
                )

                conversion_rate = float(
                    rng.uniform(0.04, 0.06)
                )

                orders = int(
                    visitors * conversion_rate
                )

                price = (
                    100.0
                    if product == "Electronics"
                    else 60.0
                )

                inventory = int(
                    rng.integers(100, 150)
                )

                units_sold = min(
                    orders,
                    inventory
                )

                revenue = (
                    units_sold * price
                )

                marketing_spend = float(
                    rng.integers(800, 1200)
                )

                returns = int(
                    rng.integers(1, 5)
                )

                rows.append(
                    {
                        "date": date,
                        "region": region,
                        "product": product,
                        "visitors": visitors,
                        "conversion_rate": conversion_rate,
                        "orders": orders,
                        "inventory": inventory,
                        "units_sold": units_sold,
                        "price": price,
                        "marketing_spend": marketing_spend,
                        "returns": returns,
                        "revenue": revenue,
                    }
                )

    return pd.DataFrame(rows)


# ---------------------------------------------------------
# Temporary test
# ---------------------------------------------------------

def inject_inventory_shortage(
    df: pd.DataFrame,
    seed: int,
    region: str,
    product: str,
    incident_start: str = "2026-08-15",
    low: int = 5,
    high: int = 15,
):
    """
    Inject an inventory shortage into one region/product segment.

    Returns:
        modified dataframe
        exact revenue impact
    """

    rng = np.random.default_rng(seed)

    df = df.copy()

    mask = (
        (df["date"] >= incident_start)
        & (df["region"] == region)
        & (df["product"] == product)
    )

    counterfactual_revenue = df.loc[
        mask,
        "revenue"
    ].copy()

    df.loc[
    mask,
    "inventory"
] = rng.integers(
    low,
    high,
    size=mask.sum()
)

    df.loc[
        mask,
        "units_sold"
    ] = np.minimum(
        df.loc[mask, "orders"],
        df.loc[mask, "inventory"],
    )

    df.loc[
        mask,
        "revenue"
    ] = (
        df.loc[mask, "units_sold"]
        * df.loc[mask, "price"]
    )

    impact = (
        counterfactual_revenue
        - df.loc[mask, "revenue"]
    ).sum()

    return df, float(impact)

def inject_conversion_drop(
    df: pd.DataFrame,
    seed: int,
    region: str,
    product: str,
    incident_start: str = "2026-08-15",
    low: float = 0.01,
    high: float = 0.02,
):
    """
    Inject a conversion-rate drop into one region/product segment.

    Returns:
        modified dataframe
        exact revenue impact
    """

    rng = np.random.default_rng(seed)

    df = df.copy()

    mask = (
        (df["date"] >= incident_start)
        & (df["region"] == region)
        & (df["product"] == product)
    )

    counterfactual_revenue = df.loc[
        mask,
        "revenue"
    ].copy()

    df.loc[
        mask,
        "conversion_rate"
    ] = rng.uniform(
        low,
        high,
        size=mask.sum()
    )

    df.loc[
        mask,
        "orders"
    ] = (
        df.loc[mask, "visitors"]
        * df.loc[mask, "conversion_rate"]
    ).astype(int)

    df.loc[
        mask,
        "units_sold"
    ] = np.minimum(
        df.loc[mask, "orders"],
        df.loc[mask, "inventory"],
    )

    df.loc[
        mask,
        "revenue"
    ] = (
        df.loc[mask, "units_sold"]
        * df.loc[mask, "price"]
    )

    impact = (
        counterfactual_revenue
        - df.loc[mask, "revenue"]
    ).sum()

    return df, float(impact)

def inject_traffic_drop(
    df: pd.DataFrame,
    region: str,
    product: str,
    incident_start: str = "2026-08-15",
    multiplier: float = 0.60,
):
    """
    Inject a traffic decline into one region/product segment.

    Returns:
        modified dataframe
        exact revenue impact
    """

    df = df.copy()

    mask = (
        (df["date"] >= incident_start)
        & (df["region"] == region)
        & (df["product"] == product)
    )

    counterfactual_revenue = df.loc[
        mask,
        "revenue"
    ].copy()

    df.loc[
        mask,
        "visitors"
    ] = (
        df.loc[mask, "visitors"]
        * multiplier
    ).astype(int)

    df.loc[
        mask,
        "orders"
    ] = (
        df.loc[mask, "visitors"]
        * df.loc[mask, "conversion_rate"]
    ).astype(int)

    df.loc[
        mask,
        "units_sold"
    ] = np.minimum(
        df.loc[mask, "orders"],
        df.loc[mask, "inventory"],
    )

    df.loc[
        mask,
        "revenue"
    ] = (
        df.loc[mask, "units_sold"]
        * df.loc[mask, "price"]
    )

    impact = (
        counterfactual_revenue
        - df.loc[mask, "revenue"]
    ).sum()

    return df, float(impact)

def inject_price_drop(
    df: pd.DataFrame,
    region: str,
    product: str,
    incident_start: str = "2026-08-15",
    multiplier: float = 0.80,
):
    """
    Inject a price decline into one region/product segment.

    Returns:
        modified dataframe
        exact revenue impact
    """

    df = df.copy()

    mask = (
        (df["date"] >= incident_start)
        & (df["region"] == region)
        & (df["product"] == product)
    )

    counterfactual_revenue = df.loc[
        mask,
        "revenue"
    ].copy()

    df.loc[
        mask,
        "price"
    ] = (
        df.loc[mask, "price"]
        * multiplier
    )

    df.loc[
        mask,
        "revenue"
    ] = (
        df.loc[mask, "units_sold"]
        * df.loc[mask, "price"]
    )

    impact = (
        counterfactual_revenue
        - df.loc[mask, "revenue"]
    ).sum()

    return df, float(impact)


if __name__ == "__main__":

    df = generate_base_data(seed=999)

    df, impact = inject_price_drop(
        df=df,
        region="North",
        product="Clothing",
        multiplier=0.80,
    )

    print("Price drop injector working.")
    print(f"Rows generated: {len(df)}")
    print(f"Injected revenue impact: {impact:.2f}")