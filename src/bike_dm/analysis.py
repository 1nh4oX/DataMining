"""Post-model analysis for stronger course interpretation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from bike_dm.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET
from bike_dm.metrics import mean_absolute_percentage_error_safe, regression_metrics


HISTORY_FEATURES = ["cnt_lag_1", "cnt_lag_24", "cnt_lag_168", "same_hour_7d_mean"]


def _dynamic_pipeline(numeric_features: list[str], random_state: int) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=200,
                    min_samples_leaf=3,
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def evaluate_history_ablation(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    random_state: int,
) -> pd.DataFrame:
    """Compare Random Forest with and without historical demand features."""
    feature_sets = {
        "all_features": NUMERIC_FEATURES,
        "without_history_features": [
            feature for feature in NUMERIC_FEATURES if feature not in HISTORY_FEATURES
        ],
    }
    rows = []
    y_train = train_df[TARGET]
    y_test = test_df[TARGET]
    for feature_set, numeric_features in feature_sets.items():
        columns = numeric_features + CATEGORICAL_FEATURES
        model = _dynamic_pipeline(numeric_features, random_state)
        model.fit(train_df[columns], y_train)
        preds = model.predict(test_df[columns])
        rows.append({"feature_set": feature_set, **regression_metrics(y_test, preds)})
    return pd.DataFrame(rows).sort_values("RMSE").reset_index(drop=True)


def _slice_metrics(df: pd.DataFrame, group_col: str, label_col: str, pred_col: str) -> list[dict]:
    rows = []
    for label, group in df.groupby(label_col, sort=True):
        rows.append(
            {
                "slice_type": group_col,
                "slice_value": str(label),
                "n": int(len(group)),
                "MAE": float(np.mean(np.abs(group["actual"] - group[pred_col]))),
                "RMSE": float(np.sqrt(np.mean((group["actual"] - group[pred_col]) ** 2))),
                "MAPE": mean_absolute_percentage_error_safe(group["actual"], group[pred_col]),
            }
        )
    return rows


def compute_error_slices(
    test_df: pd.DataFrame,
    predictions_df: pd.DataFrame,
    best_model_name: str,
) -> pd.DataFrame:
    """Compute interpretable error slices for PPT analysis."""
    joined = test_df.reset_index(drop=True).copy()
    joined["actual"] = predictions_df["actual"].to_numpy()
    joined[best_model_name] = predictions_df[best_model_name].to_numpy()
    joined["peak_label"] = joined["is_peak_hour"].map({0: "Off-peak", 1: "Peak"})
    joined["day_type"] = joined["is_weekend"].map({0: "Weekday", 1: "Weekend"})
    joined["weather_situation"] = joined["weathersit"].map(
        {
            1: "Clear or partly cloudy",
            2: "Mist or cloudy",
            3: "Light rain or snow",
            4: "Heavy rain or severe weather",
        }
    )

    rows: list[dict] = []
    rows.extend(_slice_metrics(joined, "peak_hour", "peak_label", best_model_name))
    rows.extend(_slice_metrics(joined, "day_type", "day_type", best_model_name))
    rows.extend(_slice_metrics(joined, "weather", "weather_situation", best_model_name))
    return pd.DataFrame(rows)

