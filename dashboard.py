"""Data preparation and business metrics for the Olist dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "order_id",
    "customer_id",
    "order_status",
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
}

DATE_COLUMNS = (
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
)


@dataclass(frozen=True)
class DeliveryKPIs:
    total_orders: int
    evaluable_deliveries: int
    on_time_rate: float | None
    median_delivery_days: float | None
    excluded_delivered_orders: int


def validate_orders(orders: pd.DataFrame) -> None:
    """Raise a useful error when the source is missing required fields."""
    missing = sorted(REQUIRED_COLUMNS.difference(orders.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def load_orders(path: str | Path) -> pd.DataFrame:
    """Load and prepare the orders CSV."""
    return prepare_orders(pd.read_csv(path))


def prepare_orders(orders: pd.DataFrame) -> pd.DataFrame:
    """Parse timestamps and derive delivery-performance fields."""
    validate_orders(orders)
    prepared = orders.copy()
    for column in DATE_COLUMNS:
        if column in prepared.columns:
            prepared[column] = pd.to_datetime(
                prepared[column], errors="coerce", format="mixed"
            )

    delivered = prepared["order_status"].eq("delivered")
    has_dates = prepared["order_delivered_customer_date"].notna() & prepared[
        "order_estimated_delivery_date"
    ].notna()
    prepared["is_evaluable_delivery"] = delivered & has_dates
    prepared["is_on_time"] = (
        prepared["is_evaluable_delivery"]
        & (
            prepared["order_delivered_customer_date"]
            <= prepared["order_estimated_delivery_date"]
        )
    )
    prepared["delivery_days"] = (
        prepared["order_delivered_customer_date"]
        - prepared["order_purchase_timestamp"]
    ).dt.total_seconds() / 86_400
    prepared["days_late"] = (
        prepared["order_delivered_customer_date"].dt.normalize()
        - prepared["order_estimated_delivery_date"].dt.normalize()
    ).dt.total_seconds() / 86_400
    return prepared


def filter_orders(
    orders: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp
) -> pd.DataFrame:
    """Filter by purchase date, including the full boundary days."""
    purchase_dates = orders["order_purchase_timestamp"].dt.normalize()
    mask = purchase_dates.between(pd.Timestamp(start_date), pd.Timestamp(end_date))
    return orders.loc[mask].copy()


def calculate_kpis(orders: pd.DataFrame) -> DeliveryKPIs:
    """Calculate headline metrics using only evaluable deliveries."""
    evaluable = orders.loc[orders["is_evaluable_delivery"]]
    delivered = orders["order_status"].eq("delivered")
    excluded = int((delivered & ~orders["is_evaluable_delivery"]).sum())
    if evaluable.empty:
        return DeliveryKPIs(len(orders), 0, None, None, excluded)
    return DeliveryKPIs(
        total_orders=len(orders),
        evaluable_deliveries=len(evaluable),
        on_time_rate=float(evaluable["is_on_time"].mean()),
        median_delivery_days=float(evaluable["delivery_days"].median()),
        excluded_delivered_orders=excluded,
    )


def monthly_delivery_performance(orders: pd.DataFrame) -> pd.DataFrame:
    """Return monthly on-time rates for months with evaluable deliveries."""
    evaluable = orders.loc[orders["is_evaluable_delivery"]].copy()
    columns = ["purchase_month", "on_time_rate", "evaluable_deliveries"]
    if evaluable.empty:
        return pd.DataFrame(columns=columns)
    evaluable["purchase_month"] = (
        evaluable["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    )
    result = (
        evaluable.groupby("purchase_month", as_index=False)
        .agg(
            on_time_rate=("is_on_time", "mean"),
            evaluable_deliveries=("order_id", "size"),
        )
        .sort_values("purchase_month")
        .reset_index(drop=True)
    )
    return result[columns]


def late_orders(orders: pd.DataFrame, limit: int = 25) -> pd.DataFrame:
    """Return the most delayed delivered orders first."""
    columns = [
        "order_id",
        "order_purchase_timestamp",
        "order_estimated_delivery_date",
        "order_delivered_customer_date",
        "days_late",
    ]
    return (
        orders.loc[orders["is_evaluable_delivery"] & orders["days_late"].gt(0), columns]
        .sort_values("days_late", ascending=False)
        .head(limit)
        .reset_index(drop=True)
    )
