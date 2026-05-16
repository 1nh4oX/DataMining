"""Model training and prediction."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from bike_dm.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET, feature_columns
from bike_dm.metrics import regression_metrics


MODEL_KEY_TO_LABEL = {
    "historical_mean": "Historical Mean",
    "linear_regression": "Linear Regression",
    "ridge": "Ridge",
    "lasso": "Lasso",
    "random_forest": "Random Forest",
    "gradient_boosting": "Gradient Boosting",
}


class HistoricalMeanRegressor(BaseEstimator, RegressorMixin):
    """Simple baseline that predicts the training target mean."""

    def fit(self, X, y):
        self.mean_ = float(np.mean(y))
        return self

    def predict(self, X):
        return np.full(shape=(len(X),), fill_value=self.mean_, dtype=float)


@dataclass
class ExperimentResult:
    metrics: pd.DataFrame
    predictions: pd.DataFrame
    best_model_name: str
    best_model: Pipeline


def make_preprocessor() -> ColumnTransformer:
    """Build a preprocessing transformer shared by all sklearn models."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def make_models(random_state: int, selected_model_keys: list[str] | None = None) -> dict[str, Pipeline]:
    """Create all required models."""
    linear_preprocessor = make_preprocessor()
    tree_preprocessor = make_preprocessor()

    models = {
        "Historical Mean": Pipeline(
            steps=[
                ("preprocess", make_preprocessor()),
                ("model", HistoricalMeanRegressor()),
            ]
        ),
        "Linear Regression": Pipeline(
            steps=[
                ("preprocess", linear_preprocessor),
                ("model", LinearRegression()),
            ]
        ),
        "Ridge": Pipeline(
            steps=[
                ("preprocess", make_preprocessor()),
                ("model", Ridge(alpha=5.0)),
            ]
        ),
        "Lasso": Pipeline(
            steps=[
                ("preprocess", make_preprocessor()),
                ("model", Lasso(alpha=0.001, max_iter=10000, random_state=random_state)),
            ]
        ),
        "Random Forest": Pipeline(
            steps=[
                ("preprocess", tree_preprocessor),
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
        ),
        "Gradient Boosting": Pipeline(
            steps=[
                ("preprocess", make_preprocessor()),
                (
                    "model",
                    GradientBoostingRegressor(
                        n_estimators=250,
                        learning_rate=0.05,
                        max_depth=3,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
    }

    if selected_model_keys is None:
        return models

    unknown = sorted(set(selected_model_keys).difference(MODEL_KEY_TO_LABEL))
    if unknown:
        raise ValueError(f"Unknown model keys in config: {unknown}")

    selected_labels = [MODEL_KEY_TO_LABEL[key] for key in selected_model_keys]
    return {label: models[label] for label in selected_labels}


def run_models(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    random_state: int,
    selected_model_keys: list[str] | None = None,
) -> ExperimentResult:
    """Train configured models and evaluate on the chronological test set."""
    X_train = train_df[feature_columns()]
    y_train = train_df[TARGET]
    X_test = test_df[feature_columns()]
    y_test = test_df[TARGET]

    metric_rows: list[dict] = []
    prediction_df = test_df[["datetime", TARGET]].rename(columns={TARGET: "actual"}).copy()
    fitted_models: dict[str, Pipeline] = {}

    for model_name, model in make_models(random_state, selected_model_keys).items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        fitted_models[model_name] = model
        prediction_df[model_name] = preds
        metric_rows.append({"model": model_name, **regression_metrics(y_test, preds)})

    metrics_df = pd.DataFrame(metric_rows).sort_values("RMSE").reset_index(drop=True)
    best_name = str(metrics_df.iloc[0]["model"])
    return ExperimentResult(
        metrics=metrics_df,
        predictions=prediction_df,
        best_model_name=best_name,
        best_model=fitted_models[best_name],
    )


def extract_feature_importance(model: Pipeline, top_n: int = 20) -> pd.DataFrame:
    """Extract feature importances from tree-based fitted models."""
    estimator = model.named_steps["model"]
    if not hasattr(estimator, "feature_importances_"):
        return pd.DataFrame(columns=["feature", "importance"])

    preprocessor = model.named_steps["preprocess"]
    feature_names = preprocessor.get_feature_names_out()
    importances = estimator.feature_importances_
    df = pd.DataFrame({"feature": feature_names, "importance": importances})

    df["feature"] = (
        df["feature"]
        .str.replace("num__", "", regex=False)
        .str.replace("cat__", "", regex=False)
    )
    return df.sort_values("importance", ascending=False).head(top_n).reset_index(drop=True)
