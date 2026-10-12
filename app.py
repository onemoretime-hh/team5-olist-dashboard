"""Team 5 Olist delivery-performance dashboard."""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from dashboard import (
    calculate_kpis,
    filter_orders,
    late_orders,
    load_orders,
    monthly_delivery_performance,
)


DATA_PATH = Path(__file__).parent / "data" / "olist_orders_dataset.csv"

st.set_page_config(
    page_title="Team 5 — Olist Delivery Performance Dashboard",
    page_icon="📦",
    layout="wide",
)


@st.cache_data
def get_orders(path: Path) -> pd.DataFrame:
    return load_orders(path)


st.title("Team 5 — Olist Delivery Performance Dashboard")
st.caption(
    "For the fulfillment operations manager deciding when to investigate "
    "delivery delays and prioritize late orders."
)

try:
    orders = get_orders(DATA_PATH)
except FileNotFoundError:
    st.error("Data file not found. Add olist_orders_dataset.csv to the data folder.")
    st.stop()
except ValueError as error:
    st.error(f"The orders data is invalid: {error}")
    st.stop()

minimum_date = orders["order_purchase_timestamp"].min().date()
maximum_date = orders["order_purchase_timestamp"].max().date()
st.info(
    f"Data: {minimum_date:%d %b %Y}–{maximum_date:%d %b %Y}, "
    "historical Kaggle snapshot. Production refresh: nightly."
)

selected_dates = st.sidebar.date_input(
    "Purchase date range",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date,
)
if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) != 2:
    st.warning("Select both a start date and an end date.")
    st.stop()

start_date, end_date = selected_dates
filtered = filter_orders(orders, pd.Timestamp(start_date), pd.Timestamp(end_date))
if filtered.empty:
    st.warning("No orders were placed in the selected date range.")
    st.stop()

kpis = calculate_kpis(filtered)
metric_columns = st.columns(3)
metric_columns[0].metric("Total Orders", f"{kpis.total_orders:,}")
metric_columns[1].metric(
    "On-time Delivery Rate",
    "—" if kpis.on_time_rate is None else f"{kpis.on_time_rate:.1%}",
)
metric_columns[2].metric(
    "Median Delivery Time",
    "—" if kpis.median_delivery_days is None else f"{kpis.median_delivery_days:.1f} days",
)

if kpis.excluded_delivered_orders:
    st.caption(
        f"{kpis.excluded_delivered_orders:,} delivered order(s) were excluded "
        "from delivery KPIs because a required delivery timestamp was missing."
    )

st.subheader("Monthly On-time Delivery Rate")
monthly = monthly_delivery_performance(filtered)
if monthly.empty:
    st.info("No evaluable delivered orders are available for the selected period.")
else:
    trend = (
        alt.Chart(monthly)
        .mark_line(point=True, color="#176B87", strokeWidth=3)
        .encode(
            x=alt.X("purchase_month:T", title="Purchase month"),
            y=alt.Y(
                "on_time_rate:Q",
                title="On-time delivery rate",
                axis=alt.Axis(format="%"),
                scale=alt.Scale(domain=[0, 1]),
            ),
            tooltip=[
                alt.Tooltip("purchase_month:T", title="Month", format="%b %Y"),
                alt.Tooltip("on_time_rate:Q", title="On-time rate", format=".1%"),
                alt.Tooltip(
                    "evaluable_deliveries:Q", title="Evaluable deliveries", format=","
                ),
            ],
        )
        .properties(height=330)
    )
    threshold = (
        alt.Chart(pd.DataFrame({"target": [0.85]}))
        .mark_rule(color="#C84B31", strokeDash=[6, 4])
        .encode(y="target:Q")
    )
    st.altair_chart(trend + threshold, width="stretch")

st.subheader("Order Status Breakdown")
status_counts = (
    filtered["order_status"]
    .value_counts()
    .rename_axis("order_status")
    .reset_index(name="orders")
)
status_chart = (
    alt.Chart(status_counts)
    .mark_bar(color="#64CCC5")
    .encode(
        x=alt.X("orders:Q", title="Orders"),
        y=alt.Y("order_status:N", title="Order status", sort="-x"),
        tooltip=["order_status:N", alt.Tooltip("orders:Q", format=",")],
    )
    .properties(height=280)
)
st.altair_chart(status_chart, width="stretch")

st.subheader("Most Delayed Orders")
delayed = late_orders(filtered, limit=25)
if delayed.empty:
    st.success("No late delivered orders are present in the selected period.")
else:
    display = delayed.copy()
    display["days_late"] = display["days_late"].round().astype(int)
    display = display.rename(
        columns={
            "order_id": "Order ID",
            "order_purchase_timestamp": "Purchased",
            "order_estimated_delivery_date": "Estimated delivery",
            "order_delivered_customer_date": "Actual delivery",
            "days_late": "Days late",
        }
    )
    st.dataframe(display, hide_index=True, width="stretch")

st.caption(
    "On-time delivery includes only delivered orders with both actual and "
    "estimated delivery timestamps. The first and final months may be incomplete."
)

