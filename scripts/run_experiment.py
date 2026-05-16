#!/usr/bin/env python3
"""Run the full modeling experiment and generate figures."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bike_dm.config import ensure_output_dirs, load_config, root_path
from bike_dm.data import load_hourly_data
from bike_dm.features import TARGET, build_features, feature_columns, split_time_ordered
from bike_dm.analysis import compute_error_slices, evaluate_history_ablation
from bike_dm.models import extract_feature_importance, make_models, run_models
from bike_dm.plots import generate_all_figures
from bike_dm.summary import write_summary


def main() -> None:
    config = load_config()
    ensure_output_dirs(config)
    if config["data"].get("target", TARGET) != TARGET:
        raise ValueError("This UCI pipeline currently supports target: cnt")

    raw_df = load_hourly_data(config)
    features_path = root_path(config["data"]["features_file"])
    features_df = build_features(raw_df)
    features_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_csv(features_path, index=False)

    train_df, test_df = split_time_ordered(features_df, config["data"]["train_ratio"])
    result = run_models(
        train_df=train_df,
        test_df=test_df,
        random_state=config["project"]["random_state"],
        selected_model_keys=config.get("models"),
    )

    tables_dir = root_path(config["outputs"]["tables_dir"])
    figures_dir = root_path(config["outputs"]["figures_dir"])
    metrics_path = tables_dir / "model_metrics.csv"
    predictions_path = tables_dir / "predictions.csv"
    importance_path = tables_dir / "feature_importance.csv"
    ablation_path = tables_dir / "history_ablation.csv"
    error_slices_path = tables_dir / "error_slices.csv"

    result.metrics.to_csv(metrics_path, index=False)
    result.predictions.to_csv(predictions_path, index=False)

    importance_df = extract_feature_importance(result.best_model)
    if importance_df.empty and result.best_model_name != "Random Forest":
        rf_model = make_models(config["project"]["random_state"])["Random Forest"]
        rf_model.fit(train_df[feature_columns()], train_df[TARGET])
        importance_df = extract_feature_importance(rf_model)
    importance_df.to_csv(importance_path, index=False)
    ablation_df = evaluate_history_ablation(train_df, test_df, config["project"]["random_state"])
    ablation_df.to_csv(ablation_path, index=False)
    error_slices_df = compute_error_slices(test_df, result.predictions, result.best_model_name)
    error_slices_df.to_csv(error_slices_path, index=False)

    figures = generate_all_figures(
        raw_df=raw_df,
        features_df=features_df,
        metrics_df=result.metrics,
        predictions_df=result.predictions,
        best_model_name=result.best_model_name,
        importance_df=importance_df,
        output_dir=figures_dir,
    )

    summary_path = write_summary(
        raw_df=raw_df,
        features_df=features_df,
        metrics_df=result.metrics,
        figures=figures,
        summary_path=config["outputs"]["summary_file"],
    )

    print(f"Wrote metrics: {metrics_path}")
    print(f"Wrote predictions: {predictions_path}")
    print(f"Wrote feature importance: {importance_path}")
    print(f"Wrote history ablation: {ablation_path}")
    print(f"Wrote error slices: {error_slices_path}")
    print(f"Wrote {len(figures)} figures under: {figures_dir}")
    print(f"Wrote summary: {summary_path}")


if __name__ == "__main__":
    main()
