"""Experiment summary generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from bike_dm.config import root_path
from bike_dm.data import describe_data_quality


def write_summary(
    raw_df: pd.DataFrame,
    features_df: pd.DataFrame,
    metrics_df: pd.DataFrame,
    figures: list[Path],
    summary_path: str | Path,
) -> Path:
    """Write a Markdown summary for PPT and paper reuse."""
    quality = describe_data_quality(raw_df)
    best = metrics_df.iloc[0]
    worst = metrics_df.iloc[-1]
    output_path = root_path(summary_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tables_dir = root_path("reports/tables")
    importance_path = tables_dir / "feature_importance.csv"
    ablation_path = tables_dir / "history_ablation.csv"
    error_slices_path = tables_dir / "error_slices.csv"

    importance = pd.read_csv(importance_path) if importance_path.exists() else pd.DataFrame()
    ablation = pd.read_csv(ablation_path) if ablation_path.exists() else pd.DataFrame()
    error_slices = pd.read_csv(error_slices_path) if error_slices_path.exists() else pd.DataFrame()

    project_root = root_path(".").resolve()
    figure_lines = "\n".join(
        f"- `{path.resolve().relative_to(project_root)}`" for path in figures
    )
    top_features = (
        ", ".join(importance.head(5)["feature"].tolist())
        if not importance.empty
        else "待生成"
    )
    if not ablation.empty and len(ablation) >= 2:
        all_features = ablation.loc[ablation["feature_set"] == "all_features"].iloc[0]
        no_history = ablation.loc[ablation["feature_set"] == "without_history_features"].iloc[0]
        ablation_text = (
            f"加入历史需求特征后，Random Forest 的 RMSE 从 "
            f"{no_history['RMSE']:.3f} 降至 {all_features['RMSE']:.3f}，"
            f"说明滞后需求是本任务中最关键的信息来源。"
        )
    else:
        ablation_text = "待生成历史特征消融结果。"

    if not error_slices.empty:
        hardest = error_slices.sort_values("MAE", ascending=False).iloc[0]
        easiest = error_slices.sort_values("MAE", ascending=True).iloc[0]
        slice_text = (
            f"误差最高的切片是 {hardest['slice_type']}={hardest['slice_value']} "
            f"(MAE={hardest['MAE']:.3f})；误差最低的切片是 "
            f"{easiest['slice_type']}={easiest['slice_value']} "
            f"(MAE={easiest['MAE']:.3f})。"
        )
    else:
        slice_text = "待生成误差切片结果。"

    content = f"""# 实验结果摘要

## 数据概况

- 原始记录数：{quality["rows"]}
- 原始字段数：{quality["columns"]}
- 缺失值总数：{quality["missing_values"]}
- 重复行数：{quality["duplicate_rows"]}
- 负需求记录数：{quality["negative_demand_rows"]}
- 特征工程后可建模记录数：{len(features_df)}

## 最优模型

当前测试集上表现最好的模型是 **{best["model"]}**：

- MAE：{best["MAE"]:.3f}
- RMSE：{best["RMSE"]:.3f}
- MAPE：{best["MAPE"]:.3%}
- R2：{best["R2"]:.3f}

相较表现最弱的 **{worst["model"]}**，最优模型说明非线性关系、历史需求滞后特征和天气/时间特征能够显著提升共享单车需求预测能力。

与 Historical Mean 基线相比，Random Forest 的 RMSE 从 {worst["RMSE"]:.3f} 降至 {best["RMSE"]:.3f}，MAE 从 {worst["MAE"]:.3f} 降至 {best["MAE"]:.3f}。

## 关键解释

- Top 5 重要特征：{top_features}
- 消融实验：{ablation_text}
- 误差切片：{slice_text}

## 可直接放入 PPT 的结论

1. 共享单车需求具有明显小时周期：通勤高峰和休闲时段模式不同，说明时间特征是关键变量。
2. 天气、温度、湿度与需求存在相关性，但单一变量不足以解释全部变化，需要多特征联合建模。
3. 历史需求滞后特征明显增强预测效果，体现时间序列数据挖掘的价值。
4. 线性模型可解释性强，适合做基线；集成树模型更擅长捕捉非线性关系。
5. 如果进一步做站点级预测，站点之间的空间依赖会成为关键，可自然扩展到 STGCN、DCRNN、Graph WaveNet 等时空图模型。

## 生成图表

{figure_lines}

## 模型指标表

见 `reports/tables/model_metrics.csv`。

## 附加分析表

- `reports/tables/history_ablation.csv`：历史需求特征消融。
- `reports/tables/error_slices.csv`：高峰/周末/天气切片误差。
"""
    output_path.write_text(content, encoding="utf-8")
    return output_path
