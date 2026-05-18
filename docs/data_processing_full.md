# 共享单车需求预测数据处理流程与结果（基于代码实现）

本文档依据代码实现，完整叙述从数据下载、清洗与特征工程、时间序列切分、建模与评估、到结果可视化与摘要导出的全过程。叙述以流水线为主线，强调每一步的输入、处理逻辑、输出与可复现实验结果。

## 1. 实验配置与总体入口

核心配置来自 `config/experiment.yaml`，主要包含：

- 数据源地址与目录：UCI Bike Sharing Dataset，原始与解压目录，处理后特征文件路径。
- 训练/测试切分比例：`train_ratio: 0.8`，严格按时间顺序切分。
- 模型列表：历史均值、线性回归、Ridge、Lasso、随机森林、梯度提升。
- 输出路径：图表目录与表格目录、实验摘要 Markdown。

流水线入口脚本：

- `scripts/download_data.py`：下载并解压数据。
- `scripts/build_features.py`：构造特征并导出为 `data/processed/hour_features.csv`。
- `scripts/run_experiment.py`：完整实验流水线（构造特征 -> 切分 -> 训练 -> 评估 -> 图表 -> 摘要）。
- `scripts/export_summary.py`：在已有结果基础上重新生成摘要。

## 2. 数据下载与加载

### 2.1 下载与解压

下载逻辑位于 `src/bike_dm/data.py` 的 `download_and_extract()`：

1. 在 `data/raw/` 保存 zip 包。
2. 解压到 `data/raw/bike_sharing_dataset/`。
3. 在解压目录递归搜索 `hour.csv`。

若未找到 `hour.csv` 会直接报错，保证数据路径稳定。

### 2.2 数据加载与字段校验

加载逻辑位于 `load_hourly_data()`：

- 读取 `hour.csv`。
- 校验必需字段集合：时间、天气、节假日、需求量等 17 个字段。
- 若缺字段会报错，防止后续模型输入不一致。

必需字段包括：
`instant`, `dteday`, `season`, `yr`, `mnth`, `hr`, `holiday`, `weekday`, `workingday`, `weathersit`, `temp`, `atemp`, `hum`, `windspeed`, `casual`, `registered`, `cnt`。

### 2.3 数据质量检查

`describe_data_quality()` 提供最基础的质量检测：

- 缺失值总数
- 重复行数
- 负需求（不可能值）行数

这些结果会写入实验摘要，用于课程汇报中的“数据质量”部分。

## 3. 特征工程与数据处理

### 3.1 时间构造与排序

特征构造入口是 `build_features()`：

1. 由 `dteday` 与 `hr` 合成 `datetime`。
2. 按 `datetime` 升序排序，保证时序一致。

### 3.2 规则特征

构造的规则特征包括：

- `is_weekend`：周末标记（weekday in {0,6}）。
- `is_peak_hour`：高峰时段标记（7-9, 17-19）。
- `temp_hum_interaction`：温度与湿度交互项。

### 3.3 历史需求滞后特征

为捕捉时序依赖，构造以下滞后特征：

- `cnt_lag_1`：前 1 小时需求。
- `cnt_lag_24`：前 24 小时需求。
- `cnt_lag_168`：前 7 天同小时需求。
- `same_hour_7d_mean`：同一小时过去 7 天均值（滚动，min_periods=3）。

这些特征严格基于历史数据构造，不引入未来信息。

### 3.4 特征列整理与缺失处理

最终特征表仅保留：

- `datetime`
- 目标变量 `cnt`
- 分类特征（季节、月份、小时、工作日等）
- 数值特征（温度、湿度、风速、交互项与滞后项）

由于滞后特征会产生空值，最终使用 `dropna()` 删除缺失行，保证训练数据完整。

最终特征文件输出为：`data/processed/hour_features.csv`。

## 4. 训练/测试切分

`split_time_ordered()` 按时间顺序切分：

- 前 80% 作为训练集。
- 后 20% 作为测试集。

这种切分方式避免了随机切分导致的“未来信息泄露”，更符合真实预测场景。

## 5. 模型输入预处理

所有模型使用统一预处理流程（`make_preprocessor()`）：

- 数值特征：`StandardScaler` 标准化。
- 类别特征：`OneHotEncoder` 独热编码（`handle_unknown=ignore`）。

这保证了线性模型和树模型的输入一致，便于公平比较。

## 6. 建模与评估

### 6.1 模型集合

模型由 `make_models()` 创建：

- Historical Mean（历史均值基线）
- Linear Regression
- Ridge（alpha=5.0）
- Lasso（alpha=0.001, max_iter=10000）
- Random Forest（n_estimators=200, min_samples_leaf=3）
- Gradient Boosting（n_estimators=250, learning_rate=0.05, max_depth=3）

### 6.2 评估指标

在 `metrics.py` 中定义：

- MAE
- RMSE
- MAPE（对真实值为 0 的样本做屏蔽）
- R2

### 6.3 训练与预测

`run_models()` 统一执行：

1. 训练所有模型。
2. 在测试集预测。
3. 汇总指标表 `model_metrics.csv`。
4. 汇总每个模型的预测曲线 `predictions.csv`。

根据 RMSE 排序后选择最优模型，并返回其模型对象供后续分析。

## 7. 结果分析与解释性增强

### 7.1 特征重要性

- 对树模型读取 `feature_importances_`。
- 若最优模型非随机森林，则额外训练随机森林用于特征重要性。
- 输出 `feature_importance.csv`。

### 7.2 历史特征消融实验

`evaluate_history_ablation()` 对随机森林做消融：

- `all_features`：完整特征。
- `without_history_features`：移除历史需求相关特征。

输出 `history_ablation.csv`，用于证明“特征工程比换模型更关键”。

### 7.3 误差切片分析

`compute_error_slices()` 对最优模型误差进行切片：

- 高峰 vs 非高峰
- 周末 vs 工作日
- 天气等级

输出 `error_slices.csv`，用于课程“决策价值”解读。

## 8. 图表生成

`plots.py` 统一设置 seaborn `crest` 风格，确保 PPT 风格一致。生成图表包括：

1. 小时需求曲线
2. 工作日/周末对比
3. 天气关系图（散点 + 箱线）
4. 相关性热力图
5. 模型 RMSE 对比
6. 预测曲线（真实 vs 预测）
7. 特征重要性条形图

输出目录：`reports/figures/`。

## 9. 实验摘要自动生成

`write_summary()` 读取：

- 数据质量统计
- 最优模型指标
- 特征重要性
- 消融结果
- 误差切片
- 图表列表

并输出 `reports/experiment_summary.md`，用于论文与 PPT 直接引用。

## 10. 实验结果（当前仓库已生成）

基于现有实验摘要，结果如下：

- 最优模型：Random Forest
- MAE：32.885
- RMSE：53.047
- MAPE：24.819%
- R2：0.942

关键解释：

- Top 5 特征集中在历史需求滞后项（`cnt_lag_1`, `same_hour_7d_mean`, `cnt_lag_168`, `cnt_lag_24`）。
- 消融实验表明：移除历史需求特征后 RMSE 从 53.047 上升到 123.352。
- 高峰时段误差更高（Peak MAE 52.540，Off-peak MAE 26.331）。

这些结论可直接用于“结果解释”和“调度决策意义”章节。

## 11. 产出文件清单（可复现实验物）

- `data/processed/hour_features.csv`：处理后特征表。
- `reports/tables/model_metrics.csv`：模型指标表。
- `reports/tables/predictions.csv`：预测结果。
- `reports/tables/feature_importance.csv`：特征重要性。
- `reports/tables/history_ablation.csv`：历史特征消融。
- `reports/tables/error_slices.csv`：误差切片。
- `reports/figures/*.png`：可直接放入 PPT 的图表。
- `reports/experiment_summary.md`：摘要输出。

## 12. 一键复现实验命令

若需要完整复现，按顺序执行：

1. `python scripts/download_data.py`
2. `python scripts/build_features.py`
3. `python scripts/run_experiment.py`

或使用 Makefile 一键运行：

- `make PYTHON=.venv/bin/python pipeline`

以上流程即可自动完成数据处理、建模、评估与输出。