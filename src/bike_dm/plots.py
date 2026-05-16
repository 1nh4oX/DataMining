"""Plotting utilities with seaborn crest styling."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from bike_dm.config import root_path


def set_crest_theme() -> None:
    """Apply the shared seaborn theme."""
    sns.set_theme(style="whitegrid")
    sns.set_palette(sns.color_palette("crest", n_colors=8))
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 220,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "axes.titlesize": 12,
            "legend.frameon": False,
        }
    )


def save_current(path: str | Path) -> Path:
    """Save the current figure and close it."""
    output_path = root_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    return output_path


def plot_hourly_demand(raw_df: pd.DataFrame, output_dir: str | Path) -> Path:
    set_crest_theme()
    fig, ax = plt.subplots(figsize=(9, 5))
    hourly = raw_df.groupby("hr", as_index=False)["cnt"].mean()
    sns.lineplot(data=hourly, x="hr", y="cnt", marker="o", linewidth=2.2, ax=ax)
    ax.set_title("Average Bike Demand by Hour")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Average rentals")
    ax.set_xticks(range(0, 24, 2))
    return save_current(Path(output_dir) / "01_hourly_demand.png")


def plot_workday_weekend(raw_df: pd.DataFrame, output_dir: str | Path) -> Path:
    set_crest_theme()
    df = raw_df.copy()
    df["day_type"] = df["weekday"].isin([0, 6]).map({True: "Weekend", False: "Weekday"})
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.lineplot(data=df, x="hr", y="cnt", hue="day_type", estimator="mean", errorbar=None, ax=ax)
    ax.set_title("Weekday vs Weekend Demand Pattern")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Average rentals")
    ax.set_xticks(range(0, 24, 2))
    return save_current(Path(output_dir) / "02_weekday_weekend.png")


def plot_weather_relationship(raw_df: pd.DataFrame, output_dir: str | Path) -> Path:
    set_crest_theme()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.scatterplot(
        data=raw_df.sample(min(len(raw_df), 2500), random_state=42),
        x="temp",
        y="cnt",
        hue="weathersit",
        palette=sns.color_palette("crest", n_colors=4),
        alpha=0.55,
        ax=axes[0],
    )
    axes[0].set_title("Temperature and Demand")
    axes[0].set_xlabel("Normalized temperature")
    axes[0].set_ylabel("Rentals")

    sns.boxplot(
        data=raw_df,
        x="weathersit",
        y="cnt",
        hue="weathersit",
        palette="crest",
        legend=False,
        ax=axes[1],
    )
    axes[1].set_title("Demand by Weather Situation")
    axes[1].set_xlabel("Weather situation")
    axes[1].set_ylabel("Rentals")
    return save_current(Path(output_dir) / "03_weather_relationship.png")


def plot_correlation_heatmap(features_df: pd.DataFrame, output_dir: str | Path) -> Path:
    set_crest_theme()
    numeric_cols = [
        "cnt",
        "temp",
        "atemp",
        "hum",
        "windspeed",
        "cnt_lag_1",
        "cnt_lag_24",
        "cnt_lag_168",
        "same_hour_7d_mean",
    ]
    corr = features_df[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr, cmap="crest", annot=True, fmt=".2f", square=True, linewidths=0.5, ax=ax)
    ax.set_title("Correlation Matrix of Demand Features")
    return save_current(Path(output_dir) / "04_correlation_heatmap.png")


def plot_model_metrics(metrics_df: pd.DataFrame, output_dir: str | Path) -> Path:
    set_crest_theme()
    fig, ax = plt.subplots(figsize=(9, 5))
    plot_df = metrics_df.sort_values("RMSE")
    sns.barplot(
        data=plot_df,
        x="RMSE",
        y="model",
        hue="model",
        palette="crest",
        legend=False,
        ax=ax,
    )
    ax.set_title("Model Comparison by RMSE")
    ax.set_xlabel("RMSE, lower is better")
    ax.set_ylabel("")
    return save_current(Path(output_dir) / "05_model_rmse_comparison.png")


def plot_prediction_curve(predictions_df: pd.DataFrame, best_model_name: str, output_dir: str | Path) -> Path:
    set_crest_theme()
    sample = predictions_df.head(336).copy()
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=sample, x="datetime", y="actual", label="Actual", linewidth=2.0, ax=ax)
    sns.lineplot(data=sample, x="datetime", y=best_model_name, label=best_model_name, linewidth=2.0, ax=ax)
    ax.set_title(f"Actual vs Predicted Demand: {best_model_name}")
    ax.set_xlabel("Test period")
    ax.set_ylabel("Rentals")
    ax.tick_params(axis="x", rotation=30)
    return save_current(Path(output_dir) / "06_prediction_curve.png")


def plot_feature_importance(importance_df: pd.DataFrame, output_dir: str | Path) -> Path | None:
    if importance_df.empty:
        return None
    set_crest_theme()
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(
        data=importance_df.sort_values("importance", ascending=True),
        x="importance",
        y="feature",
        hue="feature",
        palette="crest",
        legend=False,
        ax=ax,
    )
    ax.set_title("Top Feature Importances")
    ax.set_xlabel("Importance")
    ax.set_ylabel("")
    return save_current(Path(output_dir) / "07_feature_importance.png")


def generate_all_figures(
    raw_df: pd.DataFrame,
    features_df: pd.DataFrame,
    metrics_df: pd.DataFrame,
    predictions_df: pd.DataFrame,
    best_model_name: str,
    importance_df: pd.DataFrame,
    output_dir: str | Path,
) -> list[Path]:
    """Generate all presentation-ready figures."""
    figures = [
        plot_hourly_demand(raw_df, output_dir),
        plot_workday_weekend(raw_df, output_dir),
        plot_weather_relationship(raw_df, output_dir),
        plot_correlation_heatmap(features_df, output_dir),
        plot_model_metrics(metrics_df, output_dir),
        plot_prediction_curve(predictions_df, best_model_name, output_dir),
    ]
    importance_path = plot_feature_importance(importance_df, output_dir)
    if importance_path:
        figures.append(importance_path)
    return figures
