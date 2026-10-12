import pandas as pd
import pytest

from dashboard import (
    calculate_kpis,
    filter_orders,
    late_orders,
    monthly_delivery_performance,
    prepare_orders,
    validate_orders,
)


def sample_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["on_time", "late", "canceled", "missing_delivery"],
            "customer_id": ["c1", "c2", "c3", "c4"],
            "order_status": ["delivered", "delivered", "canceled", "delivered"],
            "order_purchase_timestamp": [
                "2018-01-01 10:00:00",
                "2018-01-31 23:59:59",
                "2018-02-15 12:00:00",
                "2018-02-20 12:00:00",
            ],
            "order_approved_at": [None, None, None, None],
            "order_delivered_carrier_date": [None, None, None, None],
            "order_delivered_customer_date": [
                "2018-01-05 10:00:00",
                "2018-02-12 23:59:59",
                None,
                None,
            ],
            "order_estimated_delivery_date": [
                "2018-01-06 00:00:00",
                "2018-02-10 00:00:00",
                "2018-03-01 00:00:00",
                "2018-03-05 00:00:00",
            ],
        }
    )


def test_validate_orders_reports_missing_required_columns() -> None:
    with pytest.raises(ValueError, match="order_status"):
        validate_orders(pd.DataFrame({"order_id": ["x"]}))


def test_prepare_orders_parses_dates_and_derives_delivery_fields() -> None:
    prepared = prepare_orders(sample_orders())

    assert pd.api.types.is_datetime64_any_dtype(prepared["order_purchase_timestamp"])
    assert bool(prepared.loc[0, "is_evaluable_delivery"])
    assert bool(prepared.loc[0, "is_on_time"])
    assert prepared.loc[1, "delivery_days"] == pytest.approx(12.0)
    assert prepared.loc[1, "days_late"] == pytest.approx(2.0)
    assert not bool(prepared.loc[3, "is_evaluable_delivery"])


def test_filter_orders_includes_both_boundary_dates() -> None:
    prepared = prepare_orders(sample_orders())

    filtered = filter_orders(prepared, pd.Timestamp("2018-01-01"), pd.Timestamp("2018-01-31"))

    assert filtered["order_id"].tolist() == ["on_time", "late"]


def test_calculate_kpis_excludes_non_evaluable_orders() -> None:
    prepared = prepare_orders(sample_orders())

    result = calculate_kpis(prepared)

    assert result.total_orders == 4
    assert result.evaluable_deliveries == 2
    assert result.on_time_rate == pytest.approx(0.5)
    assert result.median_delivery_days == pytest.approx(8.0)
    assert result.excluded_delivered_orders == 1


def test_calculate_kpis_returns_none_without_evaluable_deliveries() -> None:
    prepared = prepare_orders(sample_orders().iloc[[2, 3]])

    result = calculate_kpis(prepared)

    assert result.total_orders == 2
    assert result.evaluable_deliveries == 0
    assert result.on_time_rate is None
    assert result.median_delivery_days is None


def test_monthly_delivery_performance_omits_months_without_evaluable_orders() -> None:
    prepared = prepare_orders(sample_orders())

    monthly = monthly_delivery_performance(prepared)

    assert monthly["purchase_month"].dt.strftime("%Y-%m").tolist() == ["2018-01"]
    assert monthly.loc[0, "on_time_rate"] == pytest.approx(0.5)
    assert monthly.loc[0, "evaluable_deliveries"] == 2


def test_late_orders_returns_only_late_deliveries_sorted_worst_first() -> None:
    raw = pd.concat(
        [
            sample_orders(),
            pd.DataFrame(
                {
                    "order_id": ["very_late"],
                    "customer_id": ["c5"],
                    "order_status": ["delivered"],
                    "order_purchase_timestamp": ["2018-01-10"],
                    "order_approved_at": [None],
                    "order_delivered_carrier_date": [None],
                    "order_delivered_customer_date": ["2018-02-20"],
                    "order_estimated_delivery_date": ["2018-02-01"],
                }
            ),
        ],
        ignore_index=True,
    )
    prepared = prepare_orders(raw)

    result = late_orders(prepared, limit=10)

    assert result["order_id"].tolist() == ["very_late", "late"]
    assert (result["days_late"] > 0).all()

