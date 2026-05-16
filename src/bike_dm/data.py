"""Data download and loading helpers."""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

import pandas as pd

from bike_dm.config import root_path


REQUIRED_HOUR_COLUMNS = {
    "instant",
    "dteday",
    "season",
    "yr",
    "mnth",
    "hr",
    "holiday",
    "weekday",
    "workingday",
    "weathersit",
    "temp",
    "atemp",
    "hum",
    "windspeed",
    "casual",
    "registered",
    "cnt",
}


def download_and_extract(config: dict) -> Path:
    """Download and extract the UCI Bike Sharing Dataset."""
    raw_dir = root_path(config["data"]["raw_dir"])
    extract_dir = root_path(config["data"]["extract_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    extract_dir.mkdir(parents=True, exist_ok=True)

    archive_path = raw_dir / "bike_sharing_dataset.zip"
    if not archive_path.exists():
        urlretrieve(config["data"]["url"], archive_path)

    with ZipFile(archive_path, "r") as zip_file:
        zip_file.extractall(extract_dir)

    hour_path = find_hour_csv(extract_dir)
    if hour_path is None:
        raise FileNotFoundError(f"Could not find hour.csv under {extract_dir}")
    return hour_path


def find_hour_csv(search_root: str | Path) -> Path | None:
    """Find hour.csv in a downloaded/extracted dataset directory."""
    root = root_path(search_root)
    candidates = sorted(root.rglob("hour.csv"))
    return candidates[0] if candidates else None


def load_hourly_data(config: dict) -> pd.DataFrame:
    """Load the hourly UCI bike sharing CSV."""
    extract_dir = root_path(config["data"]["extract_dir"])
    hour_path = find_hour_csv(extract_dir)
    if hour_path is None:
        raise FileNotFoundError(
            "hour.csv was not found. Run: python scripts/download_data.py"
        )

    df = pd.read_csv(hour_path)
    missing = REQUIRED_HOUR_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"hour.csv is missing columns: {sorted(missing)}")
    return df


def describe_data_quality(df: pd.DataFrame) -> dict[str, int]:
    """Return simple data quality checks for reporting."""
    duplicate_rows = int(df.duplicated().sum())
    missing_values = int(df.isna().sum().sum())
    impossible_counts = int((df["cnt"] < 0).sum())
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "duplicate_rows": duplicate_rows,
        "missing_values": missing_values,
        "negative_demand_rows": impossible_counts,
    }

