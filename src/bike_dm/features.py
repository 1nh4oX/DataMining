"""Feature engineering for hourly bike sharing demand."""

from __future__ import annotations

import pandas as pd


CATEGORICAL_FEATURES = [
    "season",
    "mnth",
    "hr",
    "holiday",
    "weekday",
    "workingday",
    "weathersit",
    "is_weekend",
    "is_peak_hour",
]

NUMERIC_FEATURES = [
    "temp",
    "atemp",
    "hum",
    "windspeed",
    "temp_hum_interaction",
    "cnt_lag_1",
    "cnt_lag_24",
    "cnt_lag_168",
    "same_hour_7d_mean",
]

TARGET = "cnt"


def build_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Create time-aware features without leaking future demand."""
    df = raw_df.copy()
    df["datetime"] = pd.to_datetime(df["dteday"]) + pd.to_timedelta(df["hr"], unit="h")
    df = df.sort_values("datetime").reset_index(drop=True)

    df["is_weekend"] = df["weekday"].isin([0, 6]).astype(int)
    df["is_peak_hour"] = df["hr"].isin([7, 8, 9, 17, 18, 19]).astype(int)
    df["temp_hum_interaction"] = df["temp"] * df["hum"]

    df["cnt_lag_1"] = df["cnt"].shift(1)
    df["cnt_lag_24"] = df["cnt"].shift(24)
    df["cnt_lag_168"] = df["cnt"].shift(168)
    df["same_hour_7d_mean"] = (
        df.groupby("hr")["cnt"].transform(
            lambda series: series.shift(1).rolling(window=7, min_periods=3).mean()
        )
    )

    feature_columns = ["datetime", TARGET] + CATEGORICAL_FEATURES + NUMERIC_FEATURES
    return df[feature_columns].dropna().reset_index(drop=True)


def split_time_ordered(
    features_df: pd.DataFrame,
    train_ratio: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split data by chronological order."""
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1")
    split_idx = int(len(features_df) * train_ratio)
    train_df = features_df.iloc[:split_idx].copy()
    test_df = features_df.iloc[split_idx:].copy()
    return train_df, test_df


def feature_columns() -> list[str]:
    """Return model input columns."""
    return CATEGORICAL_FEATURES + NUMERIC_FEATURES
