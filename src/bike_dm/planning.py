"""Decision-support rules for aggregate bike-sharing supply planning.

The current UCI dataset contains demand observations, but it does not contain
station inventory or vehicle locations.  This module therefore implements an
explicit, aggregate-level planning rule rather than claiming to solve a
station-level routing problem.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


def _validate_inputs(
    predictions: pd.DataFrame,
    service_level: float,
    safety_buffer_ratio: float,
) -> None:
    """Validate public function inputs before producing planning output."""
    if "predicted_demand" not in predictions.columns:
        raise ValueError("predictions must contain a 'predicted_demand' column")
    if not 0 < service_level <= 1:
        raise ValueError("service_level must be greater than 0 and at most 1")
    if safety_buffer_ratio < 0:
        raise ValueError("safety_buffer_ratio must be non-negative")

    demand = pd.to_numeric(predictions["predicted_demand"], errors="coerce")
    if demand.isna().any():
        raise ValueError("predicted_demand must contain only numeric values")
    if (demand < 0).any():
        raise ValueError("predicted_demand cannot contain negative values")


def _as_supply_series(
    available_supply: float | Iterable[float] | pd.Series | None,
    index: pd.Index,
    demand: pd.Series,
) -> pd.Series:
    """Return an available-supply series aligned to the prediction rows.

    When no inventory assumption is supplied, the recommendation itself is
    used as the planning baseline.  This keeps the output useful for a first
    aggregate-level experiment while making the assumption deterministic.
    """
    if available_supply is None:
        return demand.copy()

    if np.isscalar(available_supply):
        value = float(available_supply)
        if value < 0:
            raise ValueError("available_supply cannot be negative")
        return pd.Series(value, index=index, dtype=float)

    series = pd.Series(available_supply, index=index, dtype=float)
    if series.isna().any() or (series < 0).any():
        raise ValueError("available_supply must contain non-negative numeric values")
    return series


def _priority(row: pd.Series) -> str:
    """Assign an explainable operational priority to one planning row."""
    if bool(row["shortage_risk"]):
        return "critical" if bool(row["is_peak_hour"]) else "high"
    if bool(row["is_peak_hour"]):
        return "watch"
    return "normal"


def calculate_supply_plan(
    predictions: pd.DataFrame,
    service_level: float = 0.90,
    safety_buffer_ratio: float = 0.10,
    available_supply: float | Iterable[float] | pd.Series | None = None,
) -> pd.DataFrame:
    """Convert demand predictions into an aggregate supply plan.

    Parameters
    ----------
    predictions:
        DataFrame containing ``predicted_demand``.  A ``datetime`` column is
        preserved when present.  ``is_peak_hour`` is optional and defaults to
        ``False`` when absent.
    service_level:
        Target service level recorded in the output for downstream scenario
        analysis.  The first rule-based version uses it as a documented policy
        target; the safety buffer remains independently configurable.
    safety_buffer_ratio:
        Fraction of predicted demand reserved as a safety buffer.
    available_supply:
        Optional scalar or row-aligned iterable representing assumed available
        supply.  If omitted, predicted demand is used as the neutral baseline,
        so shortage flags only become meaningful once an inventory assumption
        is supplied.

    Returns
    -------
    pandas.DataFrame
        A copy of the input with planning fields appended.  All quantities are
        non-negative and vehicle quantities are rounded up to whole units.
    """
    _validate_inputs(predictions, service_level, safety_buffer_ratio)
    result = predictions.copy().reset_index(drop=True)
    demand = pd.to_numeric(result["predicted_demand"], errors="raise").astype(float)

    result["service_level_target"] = float(service_level)
    result["safety_buffer_ratio"] = float(safety_buffer_ratio)
    result["safety_buffer"] = np.ceil(demand * safety_buffer_ratio).astype(int)
    result["recommended_supply"] = np.ceil(demand + result["safety_buffer"]).astype(int)

    baseline = _as_supply_series(available_supply, result.index, demand)
    result["available_supply"] = baseline.to_numpy()
    result["shortage_amount"] = np.maximum(
        result["recommended_supply"] - result["available_supply"], 0
    ).astype(int)
    result["surplus_amount"] = np.maximum(
        result["available_supply"] - result["recommended_supply"], 0
    ).astype(int)
    result["shortage_risk"] = result["available_supply"] < result["recommended_supply"]

    if "is_peak_hour" in result.columns:
        result["is_peak_hour"] = result["is_peak_hour"].astype(bool)
    else:
        result["is_peak_hour"] = False
    result["planning_priority"] = result.apply(_priority, axis=1)
    return result


def summarize_supply_plan(plan: pd.DataFrame) -> pd.DataFrame:
    """Return a compact management summary for one supply plan."""
    required = {"recommended_supply", "shortage_risk", "shortage_amount"}
    missing = required.difference(plan.columns)
    if missing:
        raise ValueError(f"plan is missing required columns: {sorted(missing)}")

    demand = pd.to_numeric(plan["predicted_demand"], errors="coerce")
    if demand.isna().any():
        raise ValueError("plan contains invalid predicted_demand values")
    total_demand = float(demand.sum())
    covered_demand = float(
        np.minimum(demand, pd.to_numeric(plan["available_supply"], errors="raise")).sum()
    )
    return pd.DataFrame(
        [
            {
                "planning_rows": int(len(plan)),
                "average_predicted_demand": float(demand.mean()) if len(plan) else 0.0,
                "average_recommended_supply": float(plan["recommended_supply"].mean())
                if len(plan)
                else 0.0,
                "stockout_risk_hours": int(plan["shortage_risk"].sum()),
                "total_shortage_amount": int(plan["shortage_amount"].sum()),
                "service_level_proxy": covered_demand / total_demand
                if total_demand > 0
                else 1.0,
            }
        ]
    )
