---
title: "refactor: 为异构数据集量身定制加载器与配置"
type: refactor
status: completed
date: 2026-03-11
---

# refactor: 为异构数据集量身定制加载器与配置 (Tailored Loaders and Config for Heterogeneous Datasets)

## 概述 (Overview)
本项目目前面临 `config/datasets.yaml` 中的配置项与 `docs/datasets/dataset_folder.txt` 记录的实际物理存储结构严重不匹配的问题。现有的 `load_wetland_dataset` 逻辑过于简单，无法处理 GWD30 的分幅瓦片、GLWD 的多类合并以及 SWAMPS 的深层嵌套结构。本任务旨在重构配置架构并实现插件化的加载器系统。

## 问题声明 / 动机 (Problem Statement / Motivation)
- **配置不匹配**：`datasets.yaml` 中的 `pattern` 和 `path` 与实际文件不符。
- **加载逻辑缺陷**：
    - **GWD30**: 每年包含数以万计的 TIF 瓦片，当前加载器只能加载单个文件。
    - **GLWD**: 每个类别是一个单独的 TIF，需要合并。
    - **SWAMPS**: 目录结构为 `stable/YYYY/MM/*.nc`，当前逻辑难以自动检索。
    - **Berkeley**: 文件名包含日期（`cyg.ddmi.YYYY-MM.l3...`），需要正确解析时间维度。
- **可维护性差**：全能型（One-size-fits-all）的 `_load_netcdf_robust` 难以应对日益增长的异构性。

## 提议的解决方案 (Proposed Solution)
1.  **重构 `config/datasets.yaml`**：引入更详细的元数据，包括 `loader_type`、`mosaic_needed`、`class_mapping` 以及针对 TOPMODEL 的分层参数。
2.  **实现加载器工厂 (Loader Factory)**：在 `loader.py` 中引入注册机制，根据数据集类型派发到专门的加载函数。
3.  **开发专项加载器**：
    - `GWD30Loader`: 使用 `rioxarray.merge` 实时合并每年数万个 TIF 瓦片。
    - `GLWDLoader`: 
        - 严格过滤非核心文件（忽略 `.tfw`, `.ovr` 等衍生品）。
        - 自动进行单位换算（例如将 `ha_x10` 除以 10.0 得到公顷）。
        - 支持按类别（`area_by_class_ha/pct`）进行动态加载和合并。
    - `TOPMODELLoader`: 
        - 支持二级分层寻址：`Config` (如 G2017_max) -> `Forcing` (如 ERA5)。
        - 自动化路径构建：`TOPMODEL/{config}/{forcing}/fwet_{config}_{forcing}_reso025_{year}.nc`。
    - `SWAMPSLoader`: 
        - 传感器感知加载：识别 `F11/ERS` (2000年前，半月频) 与 `F13/QUIKSCAT` (2000年后，日频)。
        - 实现智能时间聚合以处理数据密度突变。
    - `BerkeleyLoader`: 增强 NetCDF 加载，自动从文件名（`cyg.ddmi.YYYY-MM...`）中重建时间维度。

## 技术方案 (Technical Approach)

### 架构 (Architecture)
- **配置驱动**：加载行为完全由 YAML 中的 `loader_type` 决定。
- **延迟加载**：利用 `xarray` 和 `dask` 确保大规模数据（如 GWD30）不会撑爆内存。
- **坐标标准化**：所有加载器统一调用 `_standardize_coords` 确保 `lat`/`lon` 命名一致。
- **严格过滤**：使用正则或通配符确保仅加载 `.nc` 或 `.tif` 核心数据，过滤所有 GIS 辅助文件。

### 实施阶段 (Implementation Phases)

#### 第一阶段：配置更新 (Foundation)
- 修正 `config/datasets.yaml` 中的所有路径和模式，使其与 `dataset_folder.txt` 严格一致。
- 增加数据集特有配置段（如 `years`, `tiles_pattern`, `classes`, `scale_factor`）。

#### 第二阶段：核心加载器重构 (Core Implementation)
- 实现 `BaseLoader` 抽象类和 `DatasetLoaderRegistry`。
- 实现专项加载器：`MosaickingLoader` (GWD30), `ClassMergingLoader` (GLWD), `HierarchicalLoader` (TOPMODEL), `SensorAwareLoader` (SWAMPS)。

#### 第三阶段：健壮性提升 (Polish & Optimization)
- 添加详细的日志和针对缺失文件的“修复建议”。
- 实现配置校验工具 `scripts/verify_dataset_paths.py`。

## 系统范围影响 (System-Wide Impact)

### 交互图 (Interaction Graph)
- `Pipeline` -> `load_wetland_dataset` -> `LoaderRegistry` -> `SpecificLoader` -> `xarray`/`rioxarray` -> `Zarr/NetCDF/TIF`。

### 错误传播 (Error Propagation)
- `FileNotFoundError` 应包含基于预期模式的“路径修复建议”。
- 优雅处理 Dask 内存预警，在日志中提示调整 `chunks` 设置。

### 状态生命周期风险 (State Lifecycle Risks)
- GWD30 的实时拼接可能较慢，考虑为高频样区建立 Zarr 缓存。

## 验收标准 (Acceptance Criteria)
- [ ] `config/datasets.yaml` 通过 `src/wetland_analysis/data/config.py` 中的增强版校验。
- [ ] GWD30 指定年份的所有瓦片能正确合并为无缝的 `xr.DataArray`。
- [ ] GLWD 成功过滤衍生文件，并为 `ha_x10` 数据应用 0.1 的比例因子。
- [ ] TOPMODEL 能够正确解析 `Config/Forcing` 路径并加载多年序列。
- [ ] SWAMPS 能够处理 2000 年前后的密度突变，不影响时间聚合分析。
- [ ] Berkeley 数据能从文件名中正确识别 2018-2025 的月度时间轴。

## 来源与参考 (Sources & References)
- **原始需求**: 用户反馈 `datasets.yaml` 与 `folder.txt` 不匹配。
- **文件结构**: `docs/datasets/dataset_folder.txt`。
- **现有代码**: `src/wetland_analysis/data/loader.py`。
