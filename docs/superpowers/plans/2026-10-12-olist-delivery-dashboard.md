# Olist Delivery Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and locally verify Team 5's Streamlit delivery-performance dashboard from the Olist orders CSV.

**Architecture:** Pure Pandas functions in `dashboard.py` load and transform order data. `app.py` calls those functions and renders Streamlit metrics, Altair charts and a delayed-order table.

**Tech Stack:** Python 3.14-compatible code, uv, Streamlit, Pandas, Altair, Pytest

**Spec:** `docs/superpowers/specs/2026-10-12-olist-delivery-dashboard-design.md`

## Global Constraints

- Use only `olist_orders_dataset.csv` as dashboard input.
- Keep all user-facing dashboard and README text in English.
- Exclude non-evaluable orders from delivery KPI denominators.
- Display the historical data period and intended nightly refresh.

## Review Focus

- Missing required columns must produce a useful validation error.
- Empty date selections must not crash metric or chart code.
- No evaluable delivered orders must produce unavailable delivery KPIs, not zero.
- Date-range filtering must include both selected boundary dates.
- Rows with missing delivery timestamps must not enter on-time calculations.

---

### Task 1: Data and metric layer

**Files:**
- Create: `tests/test_dashboard.py`
- Create: `dashboard.py`

**Interfaces:**
- Produces: `validate_orders`, `prepare_orders`, `filter_orders`, `calculate_kpis`, `monthly_delivery_performance`, `late_orders`.

- [ ] Write tests for validation, date preparation, inclusive filtering, KPI denominators, empty/evaluable edge cases, monthly aggregation and late-order sorting.
- [ ] Run `uv run pytest tests/test_dashboard.py -v` and confirm failure because `dashboard` does not exist.
- [ ] Implement the minimal Pandas functions in `dashboard.py`.
- [ ] Run `uv run pytest tests/test_dashboard.py -v` and confirm all tests pass.
- [ ] Commit the task.

### Task 2: Streamlit application and project documentation

**Files:**
- Create: `app.py`
- Create: `README.md`
- Create: `pyproject.toml`
- Create: `.streamlit/config.toml`
- Create: `data/olist_orders_dataset.csv`

**Interfaces:**
- Consumes: all public functions produced by Task 1.
- Produces: a local Streamlit entry point and setup instructions.

- [ ] Add a static smoke test asserting the required page copy and dashboard calls exist.
- [ ] Run the smoke test and confirm it fails because `app.py` does not exist.
- [ ] Implement the Streamlit page, download the official Kaggle CSV, and document setup and assignment rationale.
- [ ] Run the full test suite and confirm all tests pass.
- [ ] Start Streamlit headlessly and verify its health endpoint responds successfully.
- [ ] Commit the task.

