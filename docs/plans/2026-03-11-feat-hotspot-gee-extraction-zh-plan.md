---
title: "feat: 热点区 GEE 提取与集成流水线集成"
type: feat
status: active
date: 2026-03-11
origin: docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md
---

# feat: 热点区 GEE 提取与集成流水线集成

## 概述
本功能将 `WetlandEnsemblePipeline` 与 `GEEFetcher` 进行集成，旨在自动化发现并利用遥感真值验证“热点区”——即全球湿地数据集中分歧最大（香农熵高）的区域。

## 问题声明 / 动机
目前，识别数据集之间的分歧需要人工检查。为了验证这些高不确定性区域的“真实情况”，我们需要一个流线型的工作流：
1. 计算研究区域的空间不确定性。
2. 识别冲突最严重的特定边界框（Bounding Boxes）。
3. 自动通过 GEE 获取高分辨率（Sentinel-2）影像，用于视觉或算法校准。

## 提议的解决方案
引入 `HotspotAnalyzer` 工具类和专门的 Jupyter Notebook (`05_hotspot_gee_extraction.ipynb`) 来编排端到端流程。

### 1. 热点识别逻辑
- 开发 `src/wetland_analysis/analysis/hotspots.py`，用于从熵图中提取 ROI 候选区。
- 实现聚类或“Top-N 窗口”搜索，以找到分歧最严重的 100km x 100km（或更小）区域。

### 2. GEE 连接器
- 将 `HotspotAnalyzer` 的输出直接链接到 `GEEFetcher.get_sentinel2_image`。
- 确保 `GEEFetcher` 正确处理 WGS84 边界框，用于 Sentinel-2 Cloud Score+ 合成。

### 3. 交互式验证
- 创建 `notebooks/05_hotspot_gee_extraction.ipynb`，按要求由用户手动执行。

## 技术考虑
- **内存效率**：使用 `xarray` 和 Dask 处理大区域，然后再裁剪到热点区。
- **坐标系统**：确保 `xarray` (lat/lon) 与 `ee.Geometry.Rectangle` 之间的正确转换。
- **GEE 认证**：利用新建立的 `gee_config.yaml` 实现零配置初始化。

## 系统范围影响
- **交互图**：`Pipeline` -> `HotspotAnalyzer` -> `GEEFetcher` -> `验证 Notebook`。
- **错误传播**：在 Notebook 中优雅地处理 GEE 超时或“未找到影像”的错误。
- **API 表面一致性**：确保 `GEEFetcher` 既能作为独立工具使用，也能支持流水线驱动的查询。

## 验收标准
- [ ] `HotspotAnalyzer` 能够从 `xarray` 熵图中识别出 Top-N 区域。
- [ ] `GEEFetcher` 成功使用 `config/gee_config.yaml` 初始化。
- [ ] `notebooks/05_hotspot_gee_extraction.ipynb` 能够从头到尾成功运行。
- [ ] Notebook 中的可视化内容包括：
    - 共识图 (Consensus map)。
    - 不确定性 (熵) 图 (Uncertainty map)。
    - 至少一个热点区的 Sentinel-2 真彩色合成图。

## 待创建/修改的 MVP 文件
- `src/wetland_analysis/analysis/hotspots.py` (新建)
- `notebooks/05_hotspot_gee_extraction.ipynb` (新建)
- `src/wetland_analysis/analysis/__init__.py` (导出新的分析器)

## 来源与参考
- **来源头脑风暴:** [docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md](docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md)
- **分幅逻辑:** [src/wetland_analysis/utils/mgrs_tiling.py](src/wetland_analysis/utils/mgrs_tiling.py)
- **GEE 集成:** [src/wetland_analysis/data/satellite_fetcher.py](src/wetland_analysis/data/satellite_fetcher.py)
