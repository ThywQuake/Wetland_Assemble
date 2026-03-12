---
title: "refactor: Tailored Loaders and Config for Heterogeneous Datasets"
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

## Proposed Solution
1.  **Refactor `config/datasets.yaml`**: Introduce detailed metadata including `loader_type`, `mosaic_needed`, `class_mapping`, and hierarchical parameters for TOPMODEL.
2.  **Implement Loader Factory**: A registration mechanism in `loader.py` to dispatch to specialized loading functions based on dataset type.
3.  **Develop Specialized Loaders**:
    - `GWD30Loader`: Real-time mosaicking of thousands of tiles per year using `rioxarray.merge`.
    - `GLWDLoader`: 
        - Strict `.tif` filtering (ignoring `.tfw`, `.ovr`, etc.).
        - Automatic unit scaling (e.g., dividing `ha_x10` values by 10.0).
        - Support for loading specific classes from `area_by_class_ha/pct` subdirectories.
    - `TOPMODELLoader`: 
        - Support for 2-layer hierarchy: `Config` (e.g., G2017_max) -> `Forcing` (e.g., ERA5).
        - Automated path construction: `TOPMODEL/{config}/{forcing}/fwet_{config}_{forcing}_reso025_{year}.nc`.
    - `SWAMPSLoader`: 
        - Sensor-aware loading: Detects `F11/ERS` (pre-2000, bi-monthly) vs `F13/QUIKSCAT` (post-2000, daily).
        - Intelligent temporal aggregation to handle density shifts.
    - `BerkeleyLoader`: Enhanced NetCDF loading with time-dimension reconstruction from filenames (`cyg.ddmi.YYYY-MM...`).

## Technical Approach

### Architecture
- **Config-Driven**: Loading behavior determined by `loader_type` in YAML.
- **Lazy Loading**: Use `xarray` and `dask` to ensure massive data (like GWD30) doesn't overflow memory.
- **Coordinate Standardization**: All loaders call `_standardize_coords` to ensure consistent `lat`/`lon` naming.
- **Strict Filtering**: Use glob patterns or regex to include only core data files (e.g., `.nc`, `.tif`) and ignore derivatives.

### Implementation Phases

#### Phase 1: Configuration Update (Foundation)
- Correct all paths and patterns in `config/datasets.yaml` based on `dataset_folder.txt`.
- Add dataset-specific configuration blocks (e.g., `years`, `tiles_pattern`, `classes`, `scale_factor`).

#### Phase 2: Core Loader Refactoring (Core Implementation)
- Implement `BaseLoader` abstract class and `DatasetLoaderRegistry`.
- Implement specialized loaders: `MosaickingLoader` (GWD30), `ClassMergingLoader` (GLWD), `HierarchicalLoader` (TOPMODEL), `SensorAwareLoader` (SWAMPS).

#### Phase 3: Robustness & Verification (Polish & Optimization)
- Add detailed logging and error suggestions for missing files.
- Implement `scripts/verify_dataset_paths.py` to validate config against local disk.

## System-Wide Impact

### Interaction Graph
- `Pipeline` -> `load_wetland_dataset` -> `LoaderRegistry` -> `SpecificLoader` -> `xarray`/`rioxarray` -> `Zarr/NetCDF/TIF`.

### Error & Failure Propagation
- `FileNotFoundError` should include "Fix Suggestions" based on the expected pattern.
- Handle Dask memory warnings by suggesting `chunks` adjustments in logs.

### State Lifecycle Risks
- Mosaicking (GWD30) can be slow; consider a caching mechanism or pre-processing to Zarr for frequently used ROIs.

## Acceptance Criteria
- [ ] `config/datasets.yaml` passes enhanced validation in `src/wetland_analysis/data/config.py`.
- [ ] GWD30 tiles for a given year are merged correctly into a seamless `xr.DataArray`.
- [ ] GLWD correctly merges class-specific `.tif` files and applies `0.1` scaling factor for `ha_x10` data.
- [ ] TOPMODEL correctly resolves `Config/Forcing` paths and loads multi-year sequences.
- [ ] SWAMPS handles the 2000-year density shift without failing temporal aggregations.
- [ ] Berkeley data correctly identifies the monthly timeline from 2018-2025.

## 来源与参考 (Sources & References)
- **原始需求**: 用户反馈 `datasets.yaml` 与 `folder.txt` 不匹配。
- **文件结构**: `docs/datasets/dataset_folder.txt`。
- **现有代码**: `src/wetland_analysis/data/loader.py`。
