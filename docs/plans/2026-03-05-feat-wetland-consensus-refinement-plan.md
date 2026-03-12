---
title: "feat: 30m Global Wetland Consensus & Remote Sensing Refinement Framework"
type: feat
status: active
date: 2026-03-05
origin: docs/brainstorms/2026-03-05-wetland-dataset-evaluation-brainstorm.md
---

# feat: 30m Global Wetland Consensus & Remote Sensing Refinement Framework

## Overview

本项目旨在通过 30m 分辨率的数据集成与遥感真值修正，提升全球/区域湿地数据的精度。
该功能将补充 `wetland_analysis` 现有功能，提供多源数据集共识分析（Consensus）、不确定性度量（Uncertainty）以及自动化的遥感真值验证流程。

(see brainstorm: docs/brainstorms/2026-03-05-wetland-dataset-evaluation-brainstorm.md)

## Problem Statement / Motivation

目前全球湿地数据集（如 GIEMS-MC, GWD30, GLWD 等）在空间分辨率、定义及分类标准上存在显著差异。单一数据集难以全面反映湿地的时空动态。
为了论文设计，需要一种方法能：
1. **融合 (Ensemble)**：利用不同数据集的互补性，产出更可靠的 30m 湿地分布图。
2. **定量评价 (Uncertainty)**：识别数据集争议大的“不确定性热点”。
3. **闭环修正 (Refinement)**：利用高分辨率卫星影像（Sentinel-2/Landsat）对争议区进行真值裁决，使结果具备更高的科学说服力。

## Proposed Solution

(see brainstorm: docs/brainstorms/2026-03-05-wetland-dataset-evaluation-brainstorm.md)

### 1. 30m 空间对齐与共识计算
- 利用 `rioxarray` 的 `reproject_match` 功能，将所有数据集统一重采样到 30m 投影坐标系（如 UTM）。
- 针对类别数据（湿地/非湿地），上采样使用 `nearest` 算法，下采样使用 `mode` 算法（见研究发现）。
- 计算**加权共识图**：$C(x) = \sum w_i \cdot D_i(x)$，其中 $w_i$ 为数据集权重，$D_i$ 为该数据集在该像素的判定值 (0/1)。

### 2. 不确定性热点识别 (Hotspot Detection)
- 实现**归一化 Shannon 熵**计算：$H_{norm} = -\frac{\sum p_i \log_2(p_i)}{\log_2(n)}$。
- 提取 $H_{norm} > 0.8$ 的区域作为“高不确定性热点 (Uncertainty Hotspots)”。
- 计算 **Confusion Index (CI)**：$CI = 1 - (p_{max1} - p_{max2})$，用于识别湿地-陆地过渡带的模糊区域。

### 3. 遥感真值修正 (Remote Sensing Refinement)
- 接入 **Google Earth Engine (GEE) Python API**，通过 `xee` 或 `geemap` 自动获取热点区域的 Sentinel-2/Landsat 影像。
- 采用 **Cloud Score+** 进行云遮蔽处理，确保获取高质量地表反射率数据。
- 实现采样点验证流程：在热点区随机生成采样点，提取影像特征用于最终真值判定。

## Technical Considerations

### 架构与设计模式 (Architecture & Patterns)
- **依赖倒置 (Dependency Inversion)**：`data/satellite_fetcher.py` 应继承自 `BaseFetcher` 抽象接口，以解耦 GEE 特定实现，方便未来扩展到其他 STAC API。
- **策略模式 (Strategy Pattern)**：针对不同分辨率的数据对齐，采用策略模式处理 `Categorical` (mode/nearest) 与 `Continuous` (bilinear) 数据。
- **模块化抽取**：将通用的地理空间对齐逻辑抽取至 `src/wetland_analysis/utils/geospatial.py`。

### 性能与可扩展性 (Performance & Scalability)
- **Dask + Zarr 架构**：针对 30m 全球尺度，强制使用 `Zarr` 进行块存储，并设置 `chunks={'x': 2048, 'y': 2048}` 以优化 I/O。
- **延迟重投影 (Lazy Reprojection)**：利用 `rioxarray` 的 Dask 集成，仅在最终写入或计算时执行重采样，避免中间过程产生海量内存占用。
- **空间索引加速**：利用 `geopandas.sindex` 快速过滤 ROI 范围内的数据集，减少无效数据读取。

### 代码质量与类型安全 (Python Standards)
- **严格类型提示**：所有新函数必须包含 PEP 484 类型注解，使用 Python 3.10+ 语法（如 `dict[str, Any]`, `str | None`）。
- **资源管理**：对 GEE 会话和文件句柄使用上下文管理器 (`with` statements)。
- **路径处理**：统一使用 `pathlib.Path` 替代 `os.path`。

### 环境配置与认证 (Environment & Auth)
- **凭据管理**：利用 `.env` 文件或环境变量管理 `GEE_PROJECT_ID` 及 `GOOGLE_APPLICATION_CREDENTIALS` 路径。严禁将私钥硬编码在 `satellite_fetcher.py` 中。
- **ROI 输入规范**：系统应支持通过 `GeoJSON` 或 `Shapefile` 路径定义初始研究区 (Region of Interest)，并在内部转换为 `ee.Geometry`。

## Scope Boundaries & Out of Scope
- **当前重点**：基于统计共识与遥感真值的评价与集成。
- **Out of Scope**：本阶段暂不涉及基于深度学习 (U-Net/Transformer) 的全自动分类模型实现。该部分内容将作为论文的“未来展望 (Future Work)”进行讨论。

## System-Wide Impact
- **数据流**: Raw Data (ROI input) -> `geospatial.py` (30m aligned) -> `consensus.py` / `uncertainty.py` -> `satellite_fetcher.py` -> RS Refined Output.
- **API 接口**: 提供 `calculate_ensemble_consensus` 和 `fetch_hotspot_imagery` 两个核心工具接口。

## Acceptance Criteria
- [ ] 支持通过 `Shapefile/GeoJSON` 输入 ROI，并实现多源数据集到 30m 的自动对齐与重采样。
- [ ] 实现归一化 Shannon 熵的计算，并支持分布式 (Zarr) 输出。
- [ ] 能够根据设定的不确定性阈值自动提取热点区域，并输出为符合行业标准的 GeoJSON。
- [ ] 集成 GEE API (Cloud Score+)，通过环境变量认证并成功拉取高质量影像。
- [ ] 核心模块通过 `mypy` 静态类型检查及单元测试。

## Sources & References

- **Origin brainstorm:** [docs/brainstorms/2026-03-05-wetland-dataset-evaluation-brainstorm.md](docs/brainstorms/2026-03-05-wetland-dataset-evaluation-brainstorm.md)
- **GEE 2026 Best Practices:** Cloud Score+ and Xee integration.
- **Geospatial Standards:** Resampling categorical data via `mode` and `nearest`.

## MVP Code Example (Pseudo)

### `src/wetland_analysis/analysis/consensus.py`

```python
import xarray as xr
import rioxarray
from rasterio.enums import Resampling

def align_to_30m(ds, reference_30m):
    """Align dataset to 30m grid using mode/nearest."""
    return ds.rio.reproject_match(reference_30m, resampling=Resampling.mode)

def calculate_consensus(datasets: list, weights: list):
    """Weighted sum of normalized datasets."""
    # Logic to stack and weight
    pass
```

### `src/wetland_analysis/analysis/uncertainty.py`

```python
import numpy as np

def calculate_shannon_entropy(p_array):
    """Calculate normalized Shannon Entropy for categorical ensemble."""
    # p_array shape: (n_classes, ...)
    entropy = -np.sum(p_array * np.log2(p_array + 1e-10), axis=0)
    return entropy / np.log2(len(p_array))
```
