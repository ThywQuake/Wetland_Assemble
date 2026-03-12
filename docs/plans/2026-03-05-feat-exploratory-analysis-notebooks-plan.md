---
title: "feat: Exploratory Analysis Jupyter Notebooks"
type: feat
status: active
date: 2026-03-05
origin: docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md
---

# feat: Exploratory Analysis Jupyter Notebooks

## Overview

本项目将交付一套 4 个 Jupyter Notebook，用于多源湿地数据的交互式探索与验证。重点支持亚马逊、东南亚、印度及非洲中北部四个核心研究区，并集成 2026 年 GEE 的 Sentinel-2 (Cloud Score+) 与 Landsat 8/9 最佳实践。

(see brainstorm: docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md)

## Problem Statement / Motivation

目前 `wetland_analysis` 库主要以 Python 脚本形式运行，缺乏直观的地理空间交互能力。为了论文设计中的样区选取与结果验证，需要：
1. **可视化验证**：直观对比 30m 结果与高分遥感影像。
2. **时空动态探索**：在交互地图上实时查看湿地淹没频率的演变。
3. **环境适配**：解决远程服务器运行 Jupyter 时交互式地图连接失效的问题。

## Proposed Solution

### 1. 环境准备与依赖 (Environment Setup)
- 增加 `geemap`, `ipyleaflet`, `jupyter-server-proxy`, `localtileserver` 依赖。
- 编写 `docs/guides/notebook-setup.md` 指导用户如何配置 `ssh -L` 隧道。

### 2. Notebook 序列实现 (Notebook Implementation)

#### [01] Dataset Comparison & Viewer
- **功能**：左右分栏对比 GWD30 与其他全球数据集（GLWD, GIEMS-MC）。
- **技术**：使用 `ipyleaflet.SplitControl`；利用 `loader_tools.py` 动态加载局部切片。

#### [02] Temporal Dynamics & Time-Series
- **功能**：绘制指定点的淹没概率随时间变化的曲线；生成研究区的动态 GIF 动画。
- **技术**：`geemap.chart` 绘制交互曲线；`geemap.sentinel2_timelapse` 快速生成动画。

#### [03] Uncertainty Hotspots Analysis
- **功能**：计算并展示归一化 Shannon 熵热力图；交互式选取并导出热点区域为 GeoJSON。
- **技术**：集成 `analysis/uncertainty.py` 的计算结果；使用 `geemap.draw_features` 进行交互采样。

#### [04] GEE Remote Sensing Refinement Flow
- **功能**：同时加载 S2 (Cloud Score+ 掩码) 与 Landsat 8/9 影像；并排对比共识判定结果。
- **技术**：实现 `linkCollection()` 算法关联 CS+ 质量带；通过 `applyScaleFactors()` 标准化 Landsat 数据。

## Technical Considerations

### 服务器交互配置 (Remote Interactive)
为了解决 `localtileserver` 在远程服务器上的代理问题，每个 Notebook 开头将包含以下配置：
```python
import os
os.environ['LOCALTILESERVER_CLIENT_PREFIX'] = 'proxy/{port}'
```

### 性能优化 (Performance)
- **Lazy Loading**: 强制使用 `chunks={'x': 2048, 'y': 2048}` 以优化 Xarray 的 Dask 调度。
- **Py-GEE Efficiency**: 优先在云端执行 `median()` 或 `medoid()` 聚合，减少传输到本地的数据量。

## System-Wide Impact
- **配置更新**: 需要在 `pyproject.toml` 中增加新的依赖。
- **文档补充**: 新增 Notebook 使用指南。

## Acceptance Criteria

- [ ] 成功安装并配置交互式绘图依赖。
- [ ] 01-04 号 Notebook 能够正确加载 `config/datasets.yaml` 定义的数据集。
- [ ] 能够在交互地图上切换 Amazon, SE Asia, India, N-C Africa 四个研究区。
- [ ] GEE 抓取流成功实现 Sentinel-2 (CS+) 与 Landsat 的双源掩码处理。
- [ ] 提供一份清晰的 SSH 端口转发配置指南。

## Implementation Phases

### Phase 1: 环境与配置
- 更新 `pyproject.toml`。
- 创建 `docs/guides/notebook-setup.md`。

### Phase 2: 基础探索模块 (Notebook 01, 02)
- 实现多源对比与时空曲线展示。

### Phase 3: 深度验证模块 (Notebook 03, 04)
- 实现不确定性热点可视化。
- 实现 GEE 遥感影像双源对齐与真值判定流。

## Sources & References
- **Origin brainstorm:** [docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md](docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md)
- **GEE 2026 Best Practices:** Cloud Score Plus (CS+) implementation logic.
- **Remote Jupyter Patterns:** `jupyter-server-proxy` for dynamic tiling.
