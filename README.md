# Team 5 — Olist Delivery Performance Dashboard

An English-language Streamlit dashboard for an Olist fulfillment operations manager. It shows whether completed deliveries met their promised dates and which historical deliveries experienced the longest delays. This is the Data App component of Assignment 4.

- **Deployed app:** [Open the dashboard](https://team5-olist-dashboard-9rn58rlzmdwnnfkjdwa6xl.streamlit.app)
- **Repository:** [onemoretime-hh/team5-olist-dashboard](https://github.com/onemoretime-hh/team5-olist-dashboard)

## Decision in one sentence

I designed this dashboard to help a fulfillment operations manager decide **whether delivery performance needs investigation and which completed late orders to review first**. The historical data supports retrospective investigation; it cannot identify which currently undelivered orders need intervention.

## Run locally

Requirements: Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run streamlit run app.py
```

Open `http://localhost:8501` if the browser does not open automatically. Run these commands from the repository root and keep the dataset at `data/olist_orders_dataset.csv`.

## Step 1 — Dataset and decision-maker

The project uses `olist_orders_dataset.csv` from the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_orders_dataset.csv). It is real, anonymized commercial data covering 99,441 orders from September 2016 to October 2018. One row represents one order. The CSV is approximately 17 MB, so it is suitable for GitHub and Streamlit Cloud.

The dashboard is designed for one person: an **Olist fulfillment operations manager**.

I selected this dataset because its order statuses and purchase, estimated-delivery and actual-delivery timestamps support clearly defined operational metrics without requiring additional tables. In a real business these values change every day and require repeated monitoring, making them appropriate for a dashboard rather than a one-off analysis. The order identifier supports case review; it is not a business performance measure.

## Step 2 — Why a dashboard

In a production version, the fulfillment operations manager would review the dashboard each morning. If the on-time delivery rate falls below 85% or decreases by more than five percentage points from the previous complete purchase month, they would investigate fulfillment bottlenecks and review delayed deliveries. I use 85% as a proposed investigation threshold, not an Olist service-level commitment established by the dataset. These checks require the manager's judgment; the current app draws the 85% line but does not send alerts or automatically calculate the month-to-month trigger.

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

I kept one purchase-date filter so that the manager can inspect a relevant order cohort without navigating many controls. The design choices behind each view are:

| View | Decision supported | Why I kept it |
| --- | --- | --- |
| Total orders | Judge the volume behind the selected period | A delivery rate based on very few orders needs different attention from one covering thousands. |
| On-time delivery rate | Decide whether to investigate reliability | It directly compares completed deliveries with the promised delivery timestamp. |
| Median delivery time | Check the typical customer wait | The median is less affected by a few very long delays than the mean. |
| Monthly on-time trend | See whether performance is worsening | A line makes changes across purchase cohorts visible; the 85% reference line gives a consistent review point. |
| Order-status breakdown | Understand the mix excluded from delivery metrics | Pending, canceled and unavailable orders should remain visible even though they are outside the on-time denominator. |
| Top 25 late deliveries | Select specific cases for retrospective investigation | A short, sorted table is practical for case review and avoids displaying every order. |

I cut revenue because the orders file does not contain order values; a meaningful sales analysis would require additional tables and a different decision scope. I also cut geographic rankings and seller comparisons because this file has no customer location or seller identifiers. I did not add a predictive score, map or extra filters: the immediate task is to recognize delivery problems and select cases for review, and those additions would require more data or create more choices without resolving that task. Operational teams would need carrier, seller and logistics-event data before attributing a delay to a specific cause.

Canceled and undelivered orders are not counted as late deliveries. Delivered orders missing an actual or estimated delivery timestamp are excluded from delivery KPI denominators and reported in a data-quality note. Monthly rates group orders by **purchase month**, not delivery month. The first and final months may be incomplete, and recent purchase cohorts can look unusually strong if slower orders have not arrived yet, so comparisons should use mature, complete cohorts. The historical snapshot does not measure today's performance.

## Step 4 — Refresh frequency

In production, source data should refresh nightly from the order and logistics systems. The operations manager should review it each morning. Real-time refresh would add cost without materially improving a process managed on a daily cadence.

An on-time delivery rate below 85%, or a decline of more than five percentage points from the previous complete month, should trigger an investigation. Data that is one day stale delays intervention; data that is one week stale could allow many late orders to reach customers before the team responds.

The included Kaggle CSV is a frozen historical snapshot and does not update automatically. `st.cache_data` caches the prepared file, but the app has no timed source refresh or ingestion job; a production implementation would need a nightly data replacement process and coordinated cache invalidation. Reloading the page is not equivalent to obtaining fresh business data.

## Metric definitions

- **On time:** actual customer delivery timestamp is on or before the estimated delivery timestamp.
- **Evaluable delivery:** status is `delivered` and both actual and estimated delivery timestamps are available.
- **Total orders:** all orders in the selected purchase-date range, including canceled and undelivered orders.
- **On-time delivery rate:** on-time evaluable deliveries divided by all evaluable deliveries; the app displays a dash if the denominator is zero.
- **Median delivery time:** median elapsed time in days from purchase to customer delivery among evaluable deliveries. A missing purchase timestamp cannot contribute an elapsed duration.
- **Days late:** calendar days between estimated and actual delivery dates.

The on-time comparison uses full timestamps, while days late uses calendar dates. Consequently, a delivery after the estimated timestamp but on the same calendar date can count as not on time while having zero calendar days late; it will not appear in the late-order table, which requires `days_late > 0`. This distinction follows the current implementation and should be agreed with operations before production use.

## Step 5 — Repository and deployment

The app entry point is `app.py`; reusable data preparation and KPI calculations live in `dashboard.py`. The tracked CSV belongs in `data/`, and `pyproject.toml` plus `uv.lock` describe the Python environment.

For Streamlit Community Cloud, select the repository in the submitting student's GitHub account, choose the branch containing the app, set the entry point to `app.py`, and use a Python version compatible with `pyproject.toml`. The notebook's first Markdown cell contains the app and repository links above. Assignment 4 requires both services to be under the submitting student's own accounts; the repository name alone does not establish account ownership.

The README records the design rationale for this implementation. Each student should review the wording and make sure it represents their own choices before submission.

## Test

```bash
uv run python -m pytest -q
```

