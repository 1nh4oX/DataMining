"""Regression metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def mean_absolute_percentage_error_safe(y_true, y_pred) -> float:
    """Compute MAPE while ignoring zero targets."""
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)
    mask = y_true_arr != 0
    if not mask.any():
        return float("nan")
    return float(np.mean(np.abs((y_true_arr[mask] - y_pred_arr[mask]) / y_true_arr[mask])))


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    """Return the project metric bundle."""
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAPE": mean_absolute_percentage_error_safe(y_true, y_pred),
        "R2": float(r2_score(y_true, y_pred)),
    }


def metrics_frame(rows: list[dict]) -> pd.DataFrame:
    """Convert metric dictionaries to a sorted table."""
    df = pd.DataFrame(rows)
    return df.sort_values(["RMSE", "MAE"]).reset_index(drop=True)
