# 共享单车需求预测数据挖掘项目

本仓库用于数据挖掘课程设计，主题为：

**城市共享单车需求预测中的数据挖掘方法实践与综述：从数据预处理与回归模型到时空建模思路**

项目优先保证可复现实验：下载 UCI Bike Sharing Dataset，完成数据探索、特征工程、回归模型与集成模型对比，并用 seaborn 的 `crest` 配色输出可直接放入 PPT 和论文的图表。

## 项目亮点

- 贴合课程主线：问题定义、数据采集、数据预处理、数据建模、评价解释、应用决策。
- 覆盖已学知识：统计描述、可视化、缺失/异常检查、规范化、线性回归、正则化、评价指标。
- 扩展高分内容：时间滞后特征、树模型特征重要性、时序预测评估、城市调度应用、GNN 前沿综述入口。
- 图表统一使用 seaborn `crest` palette/cmap，便于 PPT 风格一致。

## 目录结构

```text
.
├── config/experiment.yaml        # 实验配置
├── docs/                         # 课程对应、PPT 大纲、论文骨架、文献矩阵
├── reports/
│   ├── figures/                  # 生成图表
│   ├── tables/                   # 模型指标表
│   └── experiment_summary.md     # 自动生成的实验摘要
├── scripts/                      # 一键下载、构建特征、训练和导出摘要
└── src/bike_dm/                  # 可复用实验代码
```

`theory/` 和课程压缩包保留在本地，不作为实验仓库内容提交。

## 环境建议

当前机器的系统 Python 是 3.14.2，部分科学计算包可能尚未完全兼容。建议使用 Python 3.11 或 3.12 创建虚拟环境：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

如果只有 `python3` 可用，也可以尝试：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

下文命令默认已经激活 `.venv`，因此 `python` 指向虚拟环境解释器。未激活虚拟环境时可以用 `.venv/bin/python` 替代。

## 一键复现实验

```bash
python scripts/download_data.py
python scripts/build_features.py
python scripts/run_experiment.py
```

或使用 Makefile：

```bash
make PYTHON=.venv/bin/python pipeline
```

运行完成后会生成：

- `reports/tables/model_metrics.csv`
- `reports/tables/predictions.csv`
- `reports/tables/feature_importance.csv`
- `reports/figures/*.png`
- `reports/experiment_summary.md`

重新运行 pipeline 会有意更新 `reports/figures/`、`reports/tables/` 和 `reports/experiment_summary.md`，这些生成物用于课程展示和论文写作，可以提交到仓库中。

## 给评分老师和展示准备的快速入口

推荐按这个顺序检查成果：

1. `reports/experiment_summary.md`：实验结论和 PPT 可用句。
2. `reports/tables/model_metrics.csv`：模型 MAE、RMSE、MAPE、R2 对比。
3. `reports/figures/05_model_rmse_comparison.png`：模型效果图。
4. `reports/figures/06_prediction_curve.png`：预测曲线图。
5. `reports/figures/07_feature_importance.png`：关键特征解释。
6. `docs/course_alignment.md`：课程知识点映射。
7. `docs/presentation_outline.md`：15 分钟汇报页级剧本。

当前实验的核心结果：

- 最优模型：Random Forest。
- 测试集表现：MAE 32.885，RMSE 53.047，MAPE 24.819%，R2 0.942。
- 相比 Historical Mean 基线，RMSE 从 231.076 降至 53.047。
- 历史需求特征消融显示，移除 lag/rolling 特征后 RMSE 上升到 123.352。
- Top 5 特征：`cnt_lag_1`、`same_hour_7d_mean`、`cnt_lag_168`、`cnt_lag_24`、`hr_7`。
- 高峰时段误差更高：Peak MAE 52.540，Off-peak MAE 26.331。

## 图表说明

所有图表由 `src/bike_dm/plots.py` 统一设置：

- `sns.set_theme(style="whitegrid")`
- 分类图使用 `sns.color_palette("crest")`
- 连续热力图使用 `cmap="crest"`

核心图表包括：

- 小时需求曲线
- 工作日/周末需求对比
- 天气与需求关系
- 相关性热力图
- 模型误差对比
- 预测值 vs 真实值曲线
- 随机森林特征重要性

## 课程展示建议

团队 PPT 不要只堆模型。推荐叙事线：

```text
城市共享单车调度问题
-> 数据从哪里来
-> 数据为什么脏
-> 如何构造时间、天气、历史需求特征
-> 模型从可解释回归到集成学习
-> 用误差和图表比较模型
-> 结果如何服务补车、站点规划和低碳出行
-> 前沿扩展到时空图神经网络
```

详见：

- `docs/course_alignment.md`
- `docs/presentation_outline.md`
- `docs/paper_outline.md`
- `docs/literature_matrix.md`
- `docs/result_interpretation.md`
