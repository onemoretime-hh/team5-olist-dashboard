# Olist Delivery Performance Dashboard Design

## Purpose

Build an English-language Streamlit dashboard for Team 5 using `olist_orders_dataset.csv`. The audience is an Olist fulfillment operations manager who needs to detect worsening delivery performance and prioritize delayed orders.

## Decision supported

If the fulfillment operations manager sees the on-time delivery rate fall below 85% or late orders increase, they will investigate fulfillment bottlenecks and prioritize delayed orders.

## Data and metric definitions

- One row represents one order.
- Total orders counts orders in the selected purchase-date range.
- On-time delivery rate is the share of evaluable delivered orders where `order_delivered_customer_date <= order_estimated_delivery_date`.
- Median delivery time is the median elapsed days from purchase to customer delivery for delivered orders with both dates.
- Undelivered and canceled orders are excluded from delivery KPI denominators and remain visible in the status chart.
- Days late is actual delivery timestamp minus estimated delivery timestamp in days.

## Page design

The page uses a wide layout. It contains the Team 5 title, an audience-and-decision caption, a purchase-date filter, three headline metrics, a monthly on-time delivery trend with an 85% threshold, an order-status breakdown, and a table of the most delayed delivered orders. It also states the observed data period and the intended nightly production refresh.

## Data risks

Partial first and final months must not be presented as complete operating periods. Delivered orders missing required timestamps are excluded and counted in a data-quality note. A filtered range with no data shows a clear message. A range with no evaluable deliveries reports delivery KPIs as unavailable rather than zero.

## Technical design

`dashboard.py` owns loading, validation, filtering and metric calculations. `app.py` owns Streamlit layout and Altair charts. Tests exercise business logic independently from Streamlit. The app reads the CSV from `data/olist_orders_dataset.csv` and can be launched with `uv run streamlit run app.py`.

## Local completion criteria

- Dependencies install with uv.
- The data file is under 25 MB.
- All unit tests pass.
- Streamlit starts locally without an exception.
- The dashboard contains the required filter, KPIs, charts, period note and refresh note.

