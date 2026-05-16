#!/usr/bin/env python3
"""Download the UCI Bike Sharing Dataset."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bike_dm.config import load_config
from bike_dm.data import download_and_extract


def main() -> None:
    config = load_config()
    hour_path = download_and_extract(config)
    print(f"Downloaded and found hourly data: {hour_path}")


if __name__ == "__main__":
    main()

