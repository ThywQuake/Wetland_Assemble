---
title: "feat: Specific Dataset Comparison & Visualization Plan"
type: feat
status: active
date: 2026-03-05
origin: docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md
---

# feat: Specific Dataset Comparison & Visualization Plan

## Overview

本项目规划了湿地分析中的具体数据集对比逻辑及可视化产出方案。重点在于如何科学地展示 30m 高分辨率数据（GWD30, Berkeley-RWAWC）与中低分辨率全球产品（GIEMS-MC, GLWD v2, WAD2M）之间的差异、共识及不确定性。

(see brainstorm: docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md)

## Comparison Matrix

| 对比组编号 | 数据集 A (基准/高分) | 数据集 B (对比/低分) | 分析类型 | 目标区域 |
| :--- | :--- | :--- | :--- | :--- |
| **C1** | **GWD30** (30m) | **GIEMS-MC** (0.25°) | 跨尺度一致性分析 | 全球典型样区 (Amazon, SE Asia) |
| **C2** | **GWD30** (30m) | **Berkeley-RWAWC** (30m) | 高分产品互校验 | 亚马逊、印度 |
| **C3** | **Ensemble** (30m) | **GLWD v2** (1km) | 静态与动态差异分析 | 非洲中北部 |
| **C4** | **Consensus** (30m) | **Landsat/S2** | 遥感真值判定 | 不确定性热点区 |

## Proposed Visualizations (The "Gallery")

### 1. 空间一致性热力图 (Spatial Agreement Map)
- **类型**：Bivariate Map (双变量地图)
- **内容**：展示 A 和 B 的重合部分（共识）、仅 A 存在的部分、仅 B 存在的部分。
- **配色**：使用高对比度配色（如：共识-深蓝，仅A-亮绿，仅B-紫红）。
- **目的**：识别数据集在湿地边界判定上的系统性偏差。

### 2. 尺度上推/下钻对比图 (Multi-scale Slice)
- **类型**：Facet Plot (分面图)
- **内容**：左图显示原始 30m 影像；中图显示聚合到 1km 的百分比图；右图显示 1km 全球产品的分类结果。
- **目的**：揭示低分辨率产品在破碎化湿地中的“小微湿地缺失”现象。

### 3. 不确定性热点分布图 (Shannon Entropy Heatmap)
- **类型**：Continuous Heatmap
- **内容**：归一化 Shannon 熵 (0-1)。
- **配色**：Hot colormap (黑-红-黄)。
- **目的**：科学量化多源数据集的争议程度，辅助确定遥感人工核查优先级。

### 4. 淹没频率/概率时间序列 (Temporal Dynamics Line)
- **类型**：Interactive Time-series Chart
- **内容**：X 轴为时间（2013-2022），Y 轴为研究区湿地面积比例或淹没频率。
- **目的**：对比不同数据集对季节性波动的捕捉能力。

## Technical Implementation suggerstions

### 数据预处理 (Preprocessing)
- **空间对齐**：统一使用 `src/wetland_analysis/utils/geospatial.py` 中的 `align_to_reference`。
- **投影选择**：区域分析使用 UTM 投影，全球分析使用 WGS84。

### 绘图库选择 (Plotting Stack)
- **静态制图**：`matplotlib` + `cartopy` (用于论文配图)。
- **交互探索**：`geemap` + `ipyleaflet.SplitControl` (用于 Notebook 演示)。
- **统计图表**：`seaborn` (用于精度指标分布)。

## Acceptance Criteria

- [ ] 实现 C1-C4 的数据对齐流水线。
- [ ] 自动化生成 4 类核心图表模板。
- [ ] 支持将交互式地图的结果一键保存为高分辨率静态 PNG。
- [ ] 确保配色方案符合 2026 年科学出版标准（色盲友好）。

## Sources & References
- **Scientific Best Practices:** MDPI (2026) multi-scale integrated analytical environments.
- **Project Tools:** `src/wetland_analysis/visualization/` (maps.py, charts.py).
