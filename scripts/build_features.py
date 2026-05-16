#!/usr/bin/env python3
"""Build processed features for modeling."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bike_dm.config import load_config, root_path
from bike_dm.data import load_hourly_data
from bike_dm.features import build_features


def main() -> None:
    config = load_config()
    raw_df = load_hourly_data(config)
    features_df = build_features(raw_df)
    output_path = root_path(config["data"]["features_file"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_csv(output_path, index=False)
    print(f"Wrote features: {output_path} ({len(features_df)} rows)")


if __name__ == "__main__":
    main()

