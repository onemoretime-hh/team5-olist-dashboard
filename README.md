# Team 5 — Olist Delivery Performance Dashboard

An English-language Streamlit dashboard for an Olist fulfillment operations manager. It monitors whether customer orders arrive by their estimated delivery dates and identifies the most delayed orders.

## Run locally

Requirements: Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run streamlit run app.py
```

Open `http://localhost:8501` if the browser does not open automatically.

## Step 1 — Dataset and decision-maker

The project uses `olist_orders_dataset.csv` from the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_orders_dataset.csv). It is real, anonymized commercial data covering 99,441 orders from September 2016 to October 2018. One row represents one order. The CSV is approximately 17 MB, so it is suitable for GitHub and Streamlit Cloud.

The dashboard is designed for one person: an **Olist fulfillment operations manager**.

We selected this dataset because its order statuses and purchase, estimated-delivery and actual-delivery timestamps support clearly defined operational metrics. In a real business these values change every day and require repeated monitoring, making them appropriate for a dashboard rather than a one-off analysis.

## Step 2 — Why a dashboard

The fulfillment operations manager reviews the dashboard each morning. If the on-time delivery rate falls below 85% or late orders increase, they investigate fulfillment bottlenecks and prioritize delayed orders.

Without the dashboard, the manager would need to export orders, clean timestamps and calculate delivery performance in a spreadsheet. That delays investigation and creates inconsistent metric definitions. A dashboard is more suitable than a weekly email because the manager needs to change the date range, inspect trends and drill into late orders. A same-day alert could complement the dashboard when the threshold is breached.

## Step 3 — What the dashboard shows

Headline metrics:

- Total orders in the selected purchase-date range.
- On-time delivery rate among evaluable delivered orders.
- Median elapsed delivery time from purchase to customer delivery.

Supporting views:

- Monthly on-time delivery rate with an 85% reference line.
- Order-status breakdown.
- The 25 most delayed delivered orders.

The dashboard does not show revenue because the orders file does not contain order values; presenting revenue would require joining another table. It also excludes geographic analysis because customer state and city are not present in this file and would not directly identify the operational cause of a delay.

Canceled and undelivered orders are not counted as late deliveries. Delivered orders missing an actual or estimated delivery timestamp are excluded from delivery KPI denominators and reported in a data-quality note. The first and final months may be incomplete, so monthly changes at the dataset boundaries should be interpreted cautiously.

## Step 4 — Refresh frequency

In production, source data should refresh nightly from the order and logistics systems. The operations manager should review it each morning. Real-time refresh would add cost without materially improving a process managed on a daily cadence.

An on-time delivery rate below 85%, or a decline of more than five percentage points from the previous complete month, should trigger an investigation. Data that is one day stale delays intervention; data that is one week stale could allow many late orders to reach customers before the team responds.

The included Kaggle CSV is a frozen historical snapshot and does not update automatically.

## Metric definitions

- **On time:** actual customer delivery timestamp is on or before the estimated delivery timestamp.
- **Evaluable delivery:** status is `delivered` and both actual and estimated delivery timestamps are available.
- **Delivery time:** elapsed time from purchase to customer delivery.
- **Days late:** calendar days between estimated and actual delivery dates.

## Test

```bash
uv run python -m pytest -q
```

