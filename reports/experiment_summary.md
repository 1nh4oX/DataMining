# 实验结果摘要

## 数据概况

- 原始记录数：17379
- 原始字段数：17
- 缺失值总数：0
- 重复行数：0
- 负需求记录数：0
- 特征工程后可建模记录数：17211

## 最优模型

当前测试集上表现最好的模型是 **Random Forest**：

- MAE：32.885
- RMSE：53.047
- MAPE：24.819%
- R2：0.942

相较表现最弱的 **Historical Mean**，最优模型说明非线性关系、历史需求滞后特征和天气/时间特征能够显著提升共享单车需求预测能力。

与 Historical Mean 基线相比，Random Forest 的 RMSE 从 231.076 降至 53.047，MAE 从 174.214 降至 32.885。

## 关键解释

- Top 5 重要特征：cnt_lag_1, same_hour_7d_mean, cnt_lag_168, cnt_lag_24, hr_7
- 消融实验：加入历史需求特征后，Random Forest 的 RMSE 从 123.352 降至 53.047，说明滞后需求是本任务中最关键的信息来源。
- 误差切片：误差最高的切片是 peak_hour=Peak (MAE=52.540)；误差最低的切片是 peak_hour=Off-peak (MAE=26.331)。

## 可直接放入 PPT 的结论

1. 共享单车需求具有明显小时周期：通勤高峰和休闲时段模式不同，说明时间特征是关键变量。
2. 天气、温度、湿度与需求存在相关性，但单一变量不足以解释全部变化，需要多特征联合建模。
3. 历史需求滞后特征明显增强预测效果，体现时间序列数据挖掘的价值。
4. 线性模型可解释性强，适合做基线；集成树模型更擅长捕捉非线性关系。
5. 如果进一步做站点级预测，站点之间的空间依赖会成为关键，可自然扩展到 STGCN、DCRNN、Graph WaveNet 等时空图模型。

## 生成图表

- `reports/figures/01_hourly_demand.png`
- `reports/figures/02_weekday_weekend.png`
- `reports/figures/03_weather_relationship.png`
- `reports/figures/04_correlation_heatmap.png`
- `reports/figures/05_model_rmse_comparison.png`
- `reports/figures/06_prediction_curve.png`
- `reports/figures/07_feature_importance.png`

## 模型指标表

见 `reports/tables/model_metrics.csv`。

## 附加分析表

- `reports/tables/history_ablation.csv`：历史需求特征消融。
- `reports/tables/error_slices.csv`：高峰/周末/天气切片误差。
