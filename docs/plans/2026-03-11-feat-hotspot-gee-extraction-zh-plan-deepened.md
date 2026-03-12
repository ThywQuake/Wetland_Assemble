---
title: "feat: 热点区 GEE 提取与集成流水线集成 (深度增强版)"
type: feat
status: active
date: 2026-03-11
origin: docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md
---

# feat: 热点区 GEE 提取与集成流水线集成 (深度增强版)

## 概述
本功能将 `WetlandEnsemblePipeline` 与 `GEEFetcher` 进行集成，旨在自动化发现并利用遥感真值验证“热 点区”——即全球湿地数据集中分歧最大（香农熵高）的区域。**该版本针对高性能计算（HPC）环境进行了优化，从 交互式 Notebook 转向适用于超大规模处理的稳健批处理脚本。**

## 问题声明 / 动机
目前，识别数据集之间的分歧需要人工检查。为了验证这些高不确定性区域的“真实情况”，我们需要一个高效的 工作流：
1. 大规模计算研究区域的空间不确定性。
2. 识别冲突最严重的特定边界框（Bounding Boxes）。
3. 自动通过 GEE 获取高分辨率（Sentinel-2）影像，用于视觉或算法验证。
4. **能够在 Jupyter 环境之外，在服务器计算节点（SLURM/PBS）上可靠运行。**

## 提议的解决方案
引入 `HotspotAnalyzer` 工具类、生产级批处理脚本 (`scripts/run_hotspot_ensemble.py`) 以及用于结果检查 的诊断 Notebook。

### 1. 热点识别逻辑
- **`src/wetland_analysis/analysis/hotspots.py`**:
    - 使用滑动窗口或聚类方法从熵图中提取 ROI 候选区。
    - 实现 `find_top_n_hotspots(entropy_da, n=5, window_size=0.1)`（度）。
    - **优化**：使用 `dask.array` 进行并行窗口计算，避免将完整的全球熵图加载到内存中。

### 2. GEE 连接器与批量提取
- 将 `HotspotAnalyzer` 的输出直接链接到 `GEEFetcher`。
- **`GEEFetcher` 增强**：添加 `batch_fetch_hotspots(hotspot_list)` 以并行处理多个导出到 Google Drive 或云存储的任务。
- 确保 GEE 认证使用 `config/gee_config.yaml`，避免在无头服务器节点上出现交互式登录提示。

### 3. 高性能批处理脚本
- **`scripts/run_hotspot_ensemble.py`**:
    - **Dask 集成**：支持 `dask-jobqueue` (用于 SLURM/PBS) 和 `dask-mpi`，实现向多个服务器节点的无缝扩展。
    - **配置**：使用 CLI 参数（通过 `argparse`）指定 ROI、时间范围和 Dask 集群设置。
    - **持久化**：将中间结果（熵、共识）保存为 **Zarr** 文件（针对 Dask 优化），以便支持任务续传。

## 技术考虑 (HPC & Dask)
- **内存管理**：
    - 将 Dask 内存限制设置得略低于物理 RAM，以防止在共享节点上被 OOM 终止。
    - 使用 `dask.distributed.performance_report` 生成无头运行的 HTML 诊断报告。
- **错误处理**：
    - 为 GEE 请求实现“故障安全”重试机制。
    - 使用 `logging` 代替 `print`，将日志捕获到服务器的 `.out` 和 `.err` 文件中。
- **检查点 (Checkpointing)**：
    - 将包含所有对齐源和指标的最终 `xarray.Dataset` 保存到 Zarr 存储中。

## 系统范围影响
- **交互图**：`run_hotspot_ensemble.py` (CLI) -> `Pipeline` -> `HotspotAnalyzer` -> `GEEFetcher`。
- **API 表面一致性**：`GEEFetcher` 和 `Pipeline` 既可以从 Notebook 调用（小 ROI），也可以从脚本调用（全球/HPC 规模）。

## 验收标准
- [x] `HotspotAnalyzer` 能够从 Dask 后端的 `xarray` 熵图中识别出 Top-N 区域。
- [x] `scripts/run_hotspot_ensemble.py` 能够在 SLURM/PBS 节点上无人工干预地运行。
- [x] 脚本生成用于性能审计的 `dask-report.html`。
- [x] 中间和最终结果以 Zarr 格式保存。
- [x] 成功从无头脚本触发至少一个 Sentinel-2 真彩色合成图的导出任务。

## 待创建/修改的 MVP 文件
- `src/wetland_analysis/analysis/hotspots.py` (新建)
- `scripts/run_hotspot_ensemble.py` (新建：HPC 入口点)
- `notebooks/05_hotspot_gee_extraction.ipynb` (仅更新用于结果查看)
- `src/wetland_analysis/analysis/__init__.py` (导出新的分析器)

## 来源与参考
- **Dask HPC 最佳实践**: 使用 `dask-mpi` 处理批处理脚本，并使用 `performance_report` 进行无头诊断。
- **Zarr 文档**: 使用 Zarr 处理来自多个 Dask Worker 的分布式写入。
- **GEE 无头认证**: 服务账号或预配置的 `gee_config.yaml`。
