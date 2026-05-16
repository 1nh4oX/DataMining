# 文献和方法矩阵

此文件用于 PPT 的“方法演进”和论文的“相关工作”部分。

| 文献/方法 | 数据/任务 | 方法家族 | 常用指标 | 核心发现 | 局限 | 支撑本项目 |
|---|---|---|---|---|---|---|
| Fanaee-T and Gama, 2014 | Bike Sharing Dataset | 事件标注与集成检测 | 回归误差、事件识别 | 背景知识能提升共享单车事件理解 | 数据不含站点空间网络 | UCI 数据来源与背景 |
| Historical Mean | 小时需求预测 | 统计基线 | MAE, RMSE | 提供最低可用比较 | 忽略周期与天气 | 证明复杂模型有效 |
| Linear Regression | 结构化表格回归 | 线性模型 | MAE, RMSE, R2 | 可解释、易作为课程基线 | 难捕捉非线性 | 对应回归课件 |
| Ridge/Lasso | 结构化表格回归 | 正则化回归 | MAE, RMSE, R2 | 控制过拟合和参数复杂度 | 特征交互仍有限 | 对应正则化章节 |
| SVR | 中小规模回归 | 核方法 | RMSE, MAPE | 可处理非线性边界 | 大数据训练成本高 | 可作为论文拓展 |
| Random Forest | 表格预测 | Bagging 集成树 | MAE, RMSE, R2 | 非线性强、可输出特征重要性 | 外推能力有限 | 本实验最佳模型 |
| Gradient Boosting | 表格预测 | Boosting 集成树 | MAE, RMSE, R2 | 精度高，适合结构化数据 | 参数敏感 | 本实验强基线 |
| LSTM/GRU | 长历史需求序列 | 深度时序模型 | RMSE, MAE | 捕捉长短期时间依赖 | 解释性弱，需要更多数据 | 后续拓展 |
| DCRNN, 2018 | 交通流预测 | 图卷积 + RNN | MAE, RMSE, MAPE | 结合空间扩散和时间依赖 | 需要图结构 | 站点级扩展动机 |
| STGCN, 2018 | 交通流预测 | 图卷积 + 时间卷积 | MAE, RMSE, MAPE | 并行建模时空依赖 | 对图构造敏感 | PPT 前沿方法 |
| Graph WaveNet, 2019 | 交通流预测 | 自适应图 + 膨胀卷积 | MAE, RMSE, MAPE | 可学习隐藏空间关系 | 训练复杂度更高 | 解释真实城市关系 |

## 建议引用

- Fanaee-T, H., and Gama, J. Event labeling combining ensemble detectors and background knowledge. 2014.
- Li, Y. et al. Diffusion Convolutional Recurrent Neural Network: Data-Driven Traffic Forecasting. ICLR 2018.
- Yu, B. et al. Spatio-Temporal Graph Convolutional Networks: A Deep Learning Framework for Traffic Forecasting. IJCAI 2018.
- Wu, Z. et al. Graph WaveNet for Deep Spatial-Temporal Graph Modeling. IJCAI 2019.

## 综述写作提示

相关工作不要写成模型列表。建议按问题复杂度递进：

1. 共享单车需求具有周期性，因此先有历史基线和线性回归。
2. 天气、节假日和高峰通勤造成非线性，因此引入树模型和集成学习。
3. 需求随时间连续变化，因此引入 RNN/LSTM/TCN。
4. 站点之间存在空间流动，因此引入图神经网络。
5. 真实系统面临突发事件、隐私和跨城市迁移，因此需要更鲁棒和可解释的方法。
