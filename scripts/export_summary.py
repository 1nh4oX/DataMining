#!/usr/bin/env python3
"""Regenerate the Markdown experiment summary."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bike_dm.config import load_config, root_path
from bike_dm.data import load_hourly_data
from bike_dm.features import build_features
from bike_dm.summary import write_summary


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
    figures_dir = root_path(config["outputs"]["figures_dir"])
    figures = sorted(figures_dir.glob("*.png"))
    output = write_summary(
        raw_df=raw_df,
        features_df=features_df,
        metrics_df=metrics_df,
        figures=figures,
        summary_path=config["outputs"]["summary_file"],
    )
    print(f"Wrote summary: {output}")


if __name__ == "__main__":
    main()

