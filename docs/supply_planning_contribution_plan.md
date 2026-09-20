# 共享单车供应规划扩展：贡献方案与 GitHub 分支流程

## 1. 项目目标

将现有的“共享单车需求预测”实验扩展为一个可解释的运营决策支持原型：

```text
历史数据
  -> 小时需求预测
  -> 需求情景与不确定性假设
  -> 服务水平/安全缓冲计算
  -> 缺车风险识别
  -> 补车优先级与调度建议
```

本扩展不声称解决真实站点级车辆调度优化。当前 UCI 数据集没有站点库存、车辆位置、调度成本和 OD 流向，因此第一阶段定位为：

> aggregate-level rebalancing decision-support prototype

即“总量级补车决策支持原型”。后续接入 Citi Bike 等站点级数据后，才进一步研究网络级优化。

## 2. 四项任务与依赖关系

四项任务必须按以下顺序完成：

```text
任务 1：规划规则模块
          |
          v
任务 2：运营情景分析
          |
          v
任务 3：管理指标与图表
          |
          v
任务 4：管理解释文档与复现实验说明
```

任务 1 提供计算逻辑，任务 2 使用规划逻辑比较不同运营假设，任务 3 将结果转化为管理指标和图表，任务 4 固化假设、边界和可复现步骤。

## 3. 任务一：新增供应规划规则模块

### 目标

把预测需求转换为建议供给量、缓冲量和潜在缺车量。

### 建议分支

```text
feature/supply-planning-rules
```

### 主要文件

```text
src/bike_dm/planning.py
tests/test_planning.py                 # 如果项目暂时没有 tests/，请新建
scripts/run_experiment.py              # 仅增加调用和结果导出
```

### 建议接口

```python
def calculate_supply_plan(
    predictions: pd.DataFrame,
    service_level: float = 0.90,
    safety_buffer_ratio: float = 0.10,
) -> pd.DataFrame:
    """根据预测需求生成总量级供应规划结果。"""
```

输出至少包含：

| 字段 | 含义 |
|---|---|
| `datetime` | 预测时段 |
| `predicted_demand` | 最优模型预测需求 |
| `safety_buffer` | 安全缓冲量 |
| `recommended_supply` | 建议可用车辆量 |
| `shortage_risk` | 是否存在缺车风险 |
| `surplus_amount` | 假设供给下的冗余量 |
| `planning_priority` | 调度优先级 |

### 规则建议

- `recommended_supply = ceil(predicted_demand * (1 + safety_buffer_ratio))`；
- `shortage_risk` 根据假设的可用供给量与预测需求比较得到；
- 工作日早高峰和晚高峰可设置为高优先级；
- 不要把假设的供给量写成真实库存，应在字段或文档中明确标记为 scenario assumption。

### 验收标准

- 输入不改变现有模型预测结果；
- 对空数据、负需求、非法服务水平参数有明确报错或处理；
- 输出 CSV 可被后续任务直接读取；
- 至少有 5 个单元测试或等价的可复现检查；
- README 或文档中明确说明“总量级原型”边界。

### 推荐提交

```text
feat(planning): add aggregate supply planning rules
test(planning): cover buffer and shortage calculations
```

## 4. 任务二：新增运营情景分析

### 目标

比较不同运营政策下的供给压力和缺车风险，而不是只报告一个模型分数。

### 建议分支

```text
feature/planning-scenarios
```

该分支应从任务一分支合并后的最新 `main` 创建。

### 三个最低情景

| 情景 | 关键假设 | 管理问题 |
|---|---|---|
| `normal_weekday` | 常规工作日、基础缓冲 | 日常需要准备多少供给 |
| `peak_protection` | 高峰时段提高服务目标 | 哪些高峰时段必须优先保障 |
| `weather_recovery` | 恶劣天气后需求恢复 | 恢复窗口需要多少预置资源 |

### 主要文件

```text
config/experiment.yaml              # 增加 scenarios 配置
src/bike_dm/planning.py              # 增加情景参数解析，不复制核心计算
scripts/run_planning_scenarios.py
reports/tables/planning_scenarios.csv
```

### 输出字段

```text
scenario
datetime
predicted_demand
service_level_target
safety_buffer_ratio
recommended_supply
shortage_risk
planning_priority
```

### 验收标准

- 情景参数来自 YAML，而不是硬编码在脚本中；
- 同一份预测结果可以重复运行全部情景；
- 每个情景都有汇总行：风险小时数、平均建议供给量、总建议调度量；
- 情景之间的差异可以由参数解释；
- 运行失败时给出清晰的配置错误信息。

### 推荐提交

```text
feat(scenarios): add weekday peak and weather recovery cases
docs(scenarios): explain operational assumptions
```

## 5. 任务三：新增管理指标与图表

### 目标

将规划结果转化为管理者可以理解的服务水平、缺货风险和资源配置指标。

### 建议分支

```text
feature/planning-metrics
```

该分支应从任务二合并后的最新 `main` 创建。

### 指标定义

| 指标 | 建议定义 | 用途 |
|---|---|---|
| `service_level_proxy` | 被建议供给覆盖的预测需求比例 | 衡量供给保障程度 |
| `stockout_risk_hours` | `shortage_risk=True` 的小时数 | 识别缺车暴露时段 |
| `average_recommended_supply` | 建议供给量均值 | 估计资源规模 |
| `peak_shortage_risk` | 高峰时段风险比例 | 支持高峰优先级决策 |
| `rebalancing_volume` | 建议补车/调度量总和 | 估计调度工作量 |

### 主要文件

```text
src/bike_dm/planning_metrics.py
src/bike_dm/plots.py                    # 新增规划图表
scripts/run_experiment.py              # 接入输出
reports/tables/planning_metrics.csv
reports/figures/planning_*.png
```

### 最低图表集

1. 预测需求与建议供给量时间序列图；
2. 三个情景的缺车风险小时数对比图；
3. 高峰/非高峰的建议供给量箱线图或柱状图；
4. 服务水平目标与建议调度量的权衡图。

### 验收标准

- 所有指标均可由 `planning_scenarios.csv` 复算；
- 图表标题、坐标轴和图例包含英文；
- 图表使用项目现有的 `crest` 风格；
- 图表不暗示站点级精度；
- 报告中同时呈现预测误差和运营指标，说明二者不是同一概念。

### 推荐提交

```text
feat(metrics): add service-level and stockout-risk summaries
feat(plots): visualize supply-demand planning trade-offs
```

## 6. 任务四：完成管理解释文档与作品集材料

### 目标

把代码、结果、假设和管理含义连接起来，形成可复现、可审阅、可用于申请材料的项目说明。

### 建议分支

```text
docs/supply-planning-case-study
```

该分支应从任务三合并后的最新 `main` 创建。

### 主要文件

```text
docs/supply_planning_extension.md
docs/supply_planning_case_study_en.md
README.md                                  # 增加扩展入口链接
```

### 文档结构

1. **Business problem**：共享单车中的需求波动与供需错配；
2. **Data and model**：UCI 数据、时间顺序切分、特征和最优模型；
3. **Decision logic**：预测如何转化为安全缓冲和补车优先级；
4. **Scenario design**：三个情景与参数；
5. **Results**：真实运行得到的表格和图表，不预先填写数字；
6. **Limitations**：缺少站点库存、车辆位置、成本和 OD 数据；
7. **Management implications**：服务水平、资源配置和运营风险；
8. **Next step**：接入站点级数据并研究网络级调度优化。

### 验收标准

- 新用户按文档可以从零运行规划扩展；
- 文档中的数字与仓库生成的 CSV 一致；
- 所有假设与限制单独列出；
- 英文版本能用管理学术语准确描述，而非只翻译代码名；
- README 能在 30 秒内引导读者找到主实验和规划扩展。

### 推荐提交

```text
docs(case-study): document bike-sharing supply planning extension
docs(readme): link planning workflow and reproducibility steps
```

## 7. GitHub 分支与合并顺序

建议只让 `main` 保持可运行，不直接在 `main` 上开发。完整顺序如下：

```text
main
  |
  +-- feature/supply-planning-rules
  |       -> PR #1 -> main
  |
  +-- feature/planning-scenarios
  |       -> PR #2 -> main
  |
  +-- feature/planning-metrics
  |       -> PR #3 -> main
  |
  +-- docs/supply-planning-case-study
          -> PR #4 -> main
```

每个分支只解决一个主题。不要把四项任务一次性提交到一个巨大 PR 中，否则很难证明每一步的实际贡献，也不利于 review。

## 8. 本地操作命令

以下命令在 `D:\GITHUB\DataMining` 中执行。仓库所有者如果使用了保护分支，可将 `origin` 替换为自己的远程名称。

```bash
git switch main
git pull --ff-only origin main

git switch -c feature/supply-planning-rules
# 完成任务一后
git add src tests scripts
git commit -m "feat(planning): add aggregate supply planning rules"
git push -u origin feature/supply-planning-rules
```

任务一合并后，依次执行：

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/planning-scenarios
git push -u origin feature/planning-scenarios
```

后续两个分支同理：

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/planning-metrics
git push -u origin feature/planning-metrics

git switch main
git pull --ff-only origin main
git switch -c docs/supply-planning-case-study
git push -u origin docs/supply-planning-case-study
```

## 9. 每个 PR 的固定模板

每次 PR 描述都使用以下结构：

```markdown
## What changed

## Why it matters for operations management

## Files changed

## How to reproduce

## Evidence
- generated table or figure
- test result

## Assumptions and limitations

## Follow-up
```

PR 标题必须对应分支任务，正文必须写清楚你亲自实现、运行和验证的部分。申请材料中只引用已经合并或有完整 PR 记录的工作。

## 10. 最终交付清单

完成四个 PR 后，仓库至少应包含：

- 一个可复用的规划计算模块；
- 三个可配置的运营情景；
- 一张规划结果明细表和一张指标汇总表；
- 四张管理解释图表；
- 一份中文方法与限制说明；
- 一份英文 case study；
- README 中的运行入口；
- 四个清晰的 commit/PR 记录。

只有在你能够解释每个公式、参数、图表和限制时，才把这些内容写入 CV 或个人陈述。
