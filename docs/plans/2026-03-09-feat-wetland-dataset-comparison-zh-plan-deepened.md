---
title: 湿地数据集质量对比分析计划 (深度增强版)
type: feat
status: active
date: 2026-03-09
origin: docs/brainstorms/2026-03-04-wetland-dataset-evaluation-brainstorm.md
---

# 湿地数据集质量对比分析计划 (深度增强版)

## 概述
本计划旨在建立一套系统的方法，用于评估和对比多个全球湿地卫星数据集的质量。本增强版引入了 2024-2026 年地理空间数据处理的最佳实践，重点解决大规模 Sentinel-2 数据获取、高效并行趋势计算以及湿地季节性干扰等核心技术难点。

## 增强总结
- **技术栈深度**: 整合了 GEE Python API (Harmonized S2), xarray (Dask-parallelized), 以及高性能趋势库 pymannkendall。
- **性能保证**: 引入了 "Tall and Skinny" 分块策略与向量化计算模式。
- **数据质量**: 升级为 Cloud Score+ 云掩膜与波段偏移纠正方案。

---

## 数据集分类与体系

| 类别 | 数据集 | 分辨率 | 核心增强策略 |
| :--- | :--- | :--- | :--- |
| **高分辨率参考** | GWD30, Sentinel-2 | 30m | 使用 Harmonized S2 纠正光谱偏移 (Baseline 04.00) |
| **中分辨率静态** | G2017, GLWD v2 | 232m - 500m | 建立基于共识类别的 Cross-walk 映射字典 |
| **粗分辨率动态** | GIEMS-MC, SWAMPS, TOPMODEL | 0.25° | 采用 xarray-zarr 存储，优化 Dask 并行读取 |

---

## 核心执行策略

### 1. 空间对齐与预处理 (Spatial Harmonization)
- **重采样策略**: 
  - 针对分类数据 (Class)：采用 **Nearest Neighbor** 或 **Mode** 统计，保持类别完整性。
  - 针对分数数据 (Fraction)：采用 **Area-Weighted Average**，确保水体面积守恒。
- **代码参考**:
  ```python
  # 使用 xarray 进行高效重采样
  ds_resampled = ds.interp(lat=target_lat, lon=target_lon, method="nearest")
  ```

### 2. 精度验证 (Accuracy Assessment)
- **混淆矩阵优化**: 针对超大规模网格，避免直接加载到内存。
  - **建议**: 利用 `dask.array.histogram` 或分块计算混淆矩阵。
- **不确定性映射**: 使用信息熵 (Entropy) 识别数据集分歧。

### 3. 时间趋势分析 (Trend Analysis) - **性能关键点**
- **分块策略 (Chunking)**: 必须采用 **"Tall and Skinny"**。
  - 设定 `time: -1` (不分块)，`x/y` 设置为 500-1000。
  - 目标：单个 Chunk 维持在 100MB-300MB。
- **去季节化处理**:
  - 由于湿地季节性强，计算前执行 `ds.resample(time='1AS').median()`。
- **并行计算代码**:
  ```python
  import xarray as xr
  from pymannkendall import original_test

  def mk_vectorized(pixel_ts):
      return original_test(pixel_ts).slope, original_test(pixel_ts).p

  stats = xr.apply_ufunc(
      mk_vectorized, ds.wetland_fraction,
      input_core_dims=[['time']],
      output_core_dims=[[], []],
      vectorize=True,
      dask='parallelized',
      output_dtypes=['float32', 'float32']
  )
  ```

---

## 参考数据获取策略 (Sentinel-2 Acquisition)

### 1. GEE 导出最佳实践 (2024+)
- **集合选择**: `COPERNICUS/S2_SR_HARMONIZED` (必须包含，以处理 2022 年后的数据偏移)。
- **高精度云掩膜**: 推荐 `GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`。阈值设为 0.6。
- **分块导出 (Grid-based Export)**: 针对大样区，将 AOI 切分为 0.5° 网格循环导出，防止 GEE 超时。

### 2. 指数增强
- **MNDWI 优先**: 使用 `(Green - SWIR) / (Green + SWIR)`。在热带地区，SWIR 波段对抑制植被和背景土壤噪声至关重要。

---

## 实施阶段 (深度版)

### 第一阶段：数据获取与工程化 (Weeks 1-2)
- [ ] **GEE 脚本编写**: 实现基于 Harmonized 集合的干湿两季中值合成导出。
- [ ] **Zarr 架构设计**: 构建支持 Dask 并行读写的数据存储层，替代传统 NetCDF。

### 第二阶段：体系映射与基线验证 (Weeks 3)
- [ ] **映射逻辑**: 在 `src/wetland_analysis/data/preprocessing.py` 中实现 `DatasetMapper` 类，支持 GLWD 33 类到 3 类的自动归并。

### 第三阶段：并行趋势运算 (Weeks 4-5)
- [ ] **分布式计算**: 在 Dask 集群上部署 Mann-Kendall 运算任务。
- [ ] **显著性分析**: 提取 $p < 0.05$ 的稳定趋势区域。

---

## 验收标准 (增强版)
- [ ] **性能指标**: 0.25° 全球数据的趋势计算应在 30 分钟内完成。
- [ ] **精度指标**: Sentinel-2 L2A 的云掩膜残留率低于 5%。
- [ ] **代码质量**: 实现高内聚的 `TrendAnalyzer` 接口，支持多种指标切换。

## 参考来源
- **GEE Documentation**: Sentinel-2 Harmonization Guidelines (2024).
- **Dask Best Practices**: Time-series chunking and task graph optimization.
- **Pymannkendall**: Vectorized statistical tests for remote sensing.
