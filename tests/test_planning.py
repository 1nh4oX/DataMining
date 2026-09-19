from __future__ import annotations

import pandas as pd
import pytest

from bike_dm.planning import calculate_supply_plan, summarize_supply_plan


def test_calculate_supply_plan_adds_buffer_and_shortage_fields() -> None:
    predictions = pd.DataFrame(
        {
            "datetime": pd.to_datetime(["2024-01-01 08:00", "2024-01-01 14:00"]),
            "predicted_demand": [100, 50],
            "is_peak_hour": [1, 0],
        }
    )

    plan = calculate_supply_plan(
        predictions,
        service_level=0.9,
        safety_buffer_ratio=0.1,
        available_supply=[100, 80],
    )

    assert plan["safety_buffer"].tolist() == [10, 5]
    assert plan["recommended_supply"].tolist() == [110, 55]
    assert plan["shortage_amount"].tolist() == [10, 0]
    assert plan["surplus_amount"].tolist() == [0, 25]
    assert plan["shortage_risk"].tolist() == [True, False]
    assert plan["planning_priority"].tolist() == ["critical", "normal"]


def test_missing_peak_flag_defaults_to_normal_priority() -> None:
    plan = calculate_supply_plan(
        pd.DataFrame({"predicted_demand": [10]}), available_supply=10
    )

    assert bool(plan.loc[0, "is_peak_hour"]) is False
    assert plan.loc[0, "planning_priority"] == "high"


def test_summary_reports_service_level_proxy() -> None:
    plan = calculate_supply_plan(
        pd.DataFrame({"predicted_demand": [100, 50]}),
        safety_buffer_ratio=0,
        available_supply=[80, 50],
    )

    summary = summarize_supply_plan(plan).iloc[0]
    assert summary["stockout_risk_hours"] == 1
    assert summary["total_shortage_amount"] == 20
    assert summary["service_level_proxy"] == pytest.approx(130 / 150)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"service_level": 0},
        {"service_level": 1.1},
        {"safety_buffer_ratio": -0.1},
    ],
)
def test_invalid_policy_parameters_raise(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        calculate_supply_plan(pd.DataFrame({"predicted_demand": [10]}), **kwargs)


def test_negative_demand_is_rejected() -> None:
    with pytest.raises(ValueError, match="negative"):
        calculate_supply_plan(pd.DataFrame({"predicted_demand": [-1]}))
