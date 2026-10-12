from pathlib import Path


def test_app_contains_required_dashboard_elements() -> None:
    source = Path("app.py").read_text(encoding="utf-8")

    required_copy = [
        "Team 5 — Olist Delivery Performance Dashboard",
        "Total Orders",
        "On-time Delivery Rate",
        "Median Delivery Time",
        "Monthly On-time Delivery Rate",
        "Order Status Breakdown",
        "Production refresh: nightly",
    ]
    for text in required_copy:
        assert text in source

