# Wetland Analysis & Ensemble Framework (30m)

本项目是一个专为高分辨率（30m）全球/区域湿地数据集成、一致性分析及遥感真值校验而设计的 Python 框架。它支持多源异构数据集（NetCDF, GeoTIFF）的自动化对齐，并集成了 2026 年最新的 Google Earth Engine (GEE) 处理流程。

---

## 🏗 核心架构与模块详解

项目代码遵循标准科研工程布局，结构如下：

```text
/
├── config/              # 配置文件 (datasets.yaml, etc.)
├── data/                # 数据目录 (raw, processed, results)
├── docs/                # 文档目录
│   ├── brainstorms/     # 脑暴文档
│   ├── datasets/        # 数据集背景资料与说明
│   ├── guides/          # 远程设置与风格指南
│   └── plans/           # 实施计划
├── notebooks/           # 交互式 Jupyter Notebooks (01-04)
├── scripts/             # 自动化验证与运维脚本
├── src/                 # 核心算法库
│   └── wetland_analysis/
│       ├── analysis/    # 湿地集成、不确定性与精度评估逻辑
│       ├── data/        # 数据加载、配置解析与 GEE 数据获取
│       ├── utils/       # MGRS 切片系统与空间地理对齐工具
│       └── visualization/ # 论文级制图与统计图表
├── tests/               # 自动化单元测试
└── pyproject.toml       # 依赖管理
```

### 1. 数据管理模块 (`src/wetland_analysis/data/`)
负责异构数据的统一加载与遥感影像抓取。

*   **`loader.py`**: 核心加载器。
    *   `load_wetland_dataset()`: 根据 `config/datasets.yaml` 自动识别格式并加载数据集为 Xarray 对象。
    *   `list_available_datasets()`: 列出当前配置支持的所有数据集（如 GWD30, GIEMS-MC 等）。
*   **`satellite_fetcher.py`**: GEE 集成工具。
    *   `GEEFetcher` (类): 封装了 GEE 初始化与凭据管理。
    *   `get_sentinel2_image()`: **2026 最佳实践**。利用 `Cloud Score+` 质量带进行自动云掩码处理，生成高清晰度中值合成影像。
*   **`config.py`**: 负责解析 YAML 配置文件，管理全局研究区 (ROI) 坐标。

### 2. 分析与算法模块 (`analysis/`)
负责湿地集成 (Ensemble) 的核心数学计算。

*   **`consensus.py`**: 集成共识计算。
    *   `calculate_weighted_consensus()`: 对多个湿地二值图进行加权求和，生成连续的共识概率图。
    *   `get_binary_consensus()`: 根据置信度阈值生成最终的集成二值图。
*   **`uncertainty.py`**: 争议热点识别。
    *   `calculate_shannon_entropy()`: 计算像素级归一化香农熵 (0-1)，量化多源数据的不确定性。
    *   `calculate_confusion_index()`: 计算混淆指数，识别湿地-陆地过渡带的模糊区域。
    *   `identify_uncertainty_hotspots()`: 自动提取熵值超过阈值（如 0.8）的争议热点。

### 3. 地理空间工具箱 (`utils/`)
处理高精度对齐与特殊的瓦片投影转换。

*   **`mgrs_tiling.py`**: **GWD30 专用对齐系统**。
    *   `GWD30TilingSystem` (类): 处理 GWD30 特有的 15m 偏移量及 109.83km 瓦片尺寸。
    *   `tile_to_extent()`: 输入代号（如 `50TMK`）输出经纬度范围。
    *   `point_to_tile()`: 输入单点坐标输出所属瓦片代号。
    *   `bbox_to_tiles()`: 输入矩形范围输出所有相交的瓦片代号列表。
*   **`geospatial.py`**: 空间重采样工具。
    *   `align_to_reference()`: 利用 `rioxarray` 实现高效的坐标对齐。支持 `mode`（针对类别数据）和 `bilinear`（针对概率数据）算法。
    *   `create_30m_grid()`: 为指定 ROI 生成标准的 30m 参考网格。

### 4. 可视化模块 (`visualization/`)
生成论文级别的静态配图与 Notebook 交互界面。

*   **`comparison.py`**: 深度对比工具。
    *   `plot_spatial_agreement()`: **双变量地图**。展示 A/B 数据集的共识与各自偏差。
    *   `plot_multiscale_comparison()`: **多尺度展示**。并排展示 30m、1km 聚合及原始低分数据。
    *   `plot_uncertainty_heatmap()`: 绘制带热点等值线的 Shannon 熵热力图。
    *   `plot_temporal_comparison()`: 绘制多数据集的时间序列趋势对比曲线。
*   **`maps.py`**: 基础制图。
    *   `plot_wetland_map()`: 基于 `cartopy` 生成符合出版标准的湿地分布图。

---

## 🚀 快速上手指南

### 1. 环境准备
本项目建议使用 `uv` 或 `conda` 管理环境：
```bash
# 安装依赖
pip install xarray rioxarray dask geemap ipyleaflet pyproj ee
```

### 2. 服务器远程访问 (必读)
若在远程服务器运行交互式 Notebook，请查阅 [Notebook Setup Guide](docs/guides/notebook-setup.md) 进行端口转发配置。

### 3. 探索性分析工作流
项目中内置了 4 个引导式 Notebook，建议按顺序运行：
1.  `01_dataset_comparison.ipynb`: 查看不同分辨率数据集的空间差异。
2.  `02_temporal_dynamics.ipynb`: 探索湿地的季节性与年际波动。
3.  `03_uncertainty_hotspots.ipynb`: 识别数据争议区并导出采样点。
4.  `04_gee_refinement_flow.ipynb`: 调用高分影像进行最终真值裁决。

---

## 🧪 验证与测试

同步代码后，请务必运行验证脚本以确保环境正确：
```bash
python scripts/verify_workflow.py
```

如需运行单元测试：
```bash
pytest tests/
```

---

## 📄 配置文件说明 (`config/datasets.yaml`)
所有数据路径、年份范围及研究区 ROI 均在此文件中定义。在服务器上运行时，请务必将 `path` 字段修改为实际的存储路径。
