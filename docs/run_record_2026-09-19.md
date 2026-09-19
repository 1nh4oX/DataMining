# DataMining 实验运行记录（2026-09-19）

## 运行环境

- 项目分支：`feature/supply-planning-rules`
- Python：`.venv` 虚拟环境
- 数据源：UCI Bike Sharing Dataset
- 运行脚本：
  - `scripts/download_data.py`
  - `scripts/build_features.py`
  - `scripts/run_experiment.py`

日志文件：

- `logs/01_download_data.log`
- `logs/02_build_features.log`
- `logs/03_run_experiment.log`

## 数据处理结果

- 原始记录数：17,379
- 原始字段数：17
- 缺失值总数：0
- 重复行数：0
- 负需求记录数：0
- 特征工程后可建模记录数：17,211

## 模型结果

| 模型 | MAE | RMSE | MAPE | R² |
|---|---:|---:|---:|---:|
| Random Forest | 32.885 | 53.047 | 24.819% | 0.942 |
| Gradient Boosting | 38.930 | 56.573 | 42.148% | 0.934 |
| Linear Regression | 51.167 | 74.570 | 63.210% | 0.885 |
| Lasso | 51.170 | 74.574 | 63.175% | 0.885 |
| Ridge | 51.233 | 74.637 | 63.212% | 0.885 |
| Historical Mean | 174.214 | 231.076 | 481.038% | -0.105 |

最优模型为 Random Forest。相较 Historical Mean，RMSE 从 231.076 降至 53.047，MAE 从 174.214 降至 32.885。

## 解释性结果

Random Forest 前五个重要特征：

1. `cnt_lag_1`
2. `same_hour_7d_mean`
3. `cnt_lag_168`
4. `cnt_lag_24`
5. `hr_7`

历史需求特征消融结果：

- 包含历史特征：RMSE 53.047
- 移除历史特征：RMSE 123.352

高峰/非高峰误差：

- Peak MAE：52.540
- Off-peak MAE：26.331

## 供应规划输出

已生成：`reports/tables/supply_plan.csv`

当前配置：

- 服务水平目标：0.90
- 安全缓冲比例：0.10

该文件将预测需求转换为安全缓冲、建议供给量、缺车量、冗余量和调度优先级。

重要边界：当前数据集没有真实库存，因此脚本未传入站点库存或车辆位置。此轮结果是总量级规划原型；后续需要接入库存假设或站点级数据，才能解释真实缺车风险和调度量。

## 生成文件

- `reports/tables/model_metrics.csv`
- `reports/tables/predictions.csv`
- `reports/tables/feature_importance.csv`
- `reports/tables/history_ablation.csv`
- `reports/tables/error_slices.csv`
- `reports/tables/supply_plan.csv`
- `reports/figures/*.png`
- `reports/experiment_summary.md`
