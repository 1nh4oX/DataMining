"""Configuration helpers for the bike sharing project."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - runtime dependency hint
    raise RuntimeError(
        "PyYAML is required. Install dependencies with: "
        "python3 -m pip install -r requirements.txt"
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "experiment.yaml"


def root_path(value: str | Path) -> Path:
    """Resolve a repo-relative path to an absolute path."""
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict[str, Any]:
    """Load the YAML experiment configuration."""
    config_path = root_path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def ensure_output_dirs(config: dict[str, Any]) -> None:
    """Create configured output directories."""
    for key in ("figures_dir", "tables_dir"):
        root_path(config["outputs"][key]).mkdir(parents=True, exist_ok=True)
    root_path(config["data"]["processed_dir"]).mkdir(parents=True, exist_ok=True)
