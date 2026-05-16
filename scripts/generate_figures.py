#!/usr/bin/env python3
"""Regenerate figures from existing experiment outputs."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bike_dm.config import load_config, root_path
from bike_dm.data import load_hourly_data
from bike_dm.features import build_features
from bike_dm.plots import generate_all_figures


def main() -> None:
    config = load_config()
    raw_df = load_hourly_data(config)
    features_path = root_path(config["data"]["features_file"])
    features_df = (
        pd.read_csv(features_path, parse_dates=["datetime"])
        if features_path.exists()
        else build_features(raw_df)
    )
    metrics_df = pd.read_csv(root_path(config["outputs"]["tables_dir"]) / "model_metrics.csv")
    predictions_df = pd.read_csv(
        root_path(config["outputs"]["tables_dir"]) / "predictions.csv",
        parse_dates=["datetime"],
    )
    importance_path = root_path(config["outputs"]["tables_dir"]) / "feature_importance.csv"
    importance_df = pd.read_csv(importance_path) if importance_path.exists() else pd.DataFrame()
    best_model_name = str(metrics_df.iloc[0]["model"])

    figures = generate_all_figures(
        raw_df=raw_df,
        features_df=features_df,
        metrics_df=metrics_df,
        predictions_df=predictions_df,
        best_model_name=best_model_name,
        importance_df=importance_df,
        output_dir=root_path(config["outputs"]["figures_dir"]),
    )
    print(f"Regenerated {len(figures)} figures.")


if __name__ == "__main__":
    main()

