# 架构评审：热点区 GEE 提取与集成流水线 (深度增强版)

## 1. 架构概述
当前的系统架构是一个基于 Python 的科学流水线 (`WetlandEnsemblePipeline`)，旨在提取多个湿地数据集，在时空上对齐它们 (`SpatioTemporalAligner`)，并使用 `xarray` 生成共识和不确定性（香农熵）图。架构中包含一个独立的 `GEEFetcher` 组件，负责向 Google Earth Engine (GEE) 进行身份验证并获取 Sentinel-2 合成影像。新计划引入了 `HotspotAnalyzer` 来连接这两者：从流水线的输出中识别高不确定性区域，并通过 `GEEFetcher` 中新的 `batch_fetch_hotspots` 方法触发 GEE 数据提取。该计划还将执行环境从交互式 Notebook 转移到了基于 Dask (`dask-jobqueue`/`dask-mpi`) 的无头 HPC 环境中。

## 2. 变更评估
建议的变更很自然地融入了现有流水线。
- `HotspotAnalyzer` 作为 `WetlandEnsemblePipeline` 输出的下游消费者运行（`run_analysis()` 返回包含 `shannon_entropy` 的 `xr.Dataset`）。
- `GEEFetcher` 被适当扩展 (`batch_fetch_hotspots`)，以支持新的面向批处理的工作流，而不仅仅是单图提取 (`get_sentinel2_image`)。
- 通过 `scripts/run_hotspot_ensemble.py` 向 HPC 的过渡是科学流水线规模化扩展的标准演进。

## 3. 合规性检查
- **单一职责原则 (SRP)**: 得到维护。`HotspotAnalyzer` 专门负责寻找热点。`GEEFetcher` 处理 GEE 交互。主脚本协调它们。
- **关注点分离**: 维护良好。流水线生成数据，分析器解释数据，脚本处理基础设施 (Dask/HPC)。
- **依赖倒置**: 计划没有明确提及接口，但保持 `HotspotAnalyzer` 与 `GEEFetcher` 内部工作原理（传递通用边界/坐标）的解耦将至关重要。

## 4. 风险分析
- **耦合风险**: 存在将 `HotspotAnalyzer` 与 GEE 特定的坐标要求 (`ee.Geometry`) 耦合过紧的风险。`HotspotAnalyzer` 应输出标准的 WGS84 边界框（例如，`[(min_lon, min_lat, max_lon, max_lat), ...]`），而 `GEEFetcher` 应负责将这些转换为 `ee.Geometry.Rectangle`。
- **Dask/Xarray 集成**: 在 `HotspotAnalyzer` 中使用 `dask.array` 进行滑动窗口计算具有技术挑战性。即使使用 Dask，标准的 `xarray.rolling` 操作也可能占用大量内存。根据窗口大小和输入 Zarr 文件的分块策略，这可能会导致 Dask worker 内存溢出。
- **GEE 速率限制**: 如果没有实现适当的节流或批处理策略，新的 `batch_fetch_hotspots` 很容易达到 GEE 并发任务或查询的限制。
- **数据持久化**: 计划提到保存为 Zarr，但在保存前确保中间步骤（对齐 -> 熵）被正确分块对于下游 `HotspotAnalyzer` 的性能至关重要。

## 5. 建议
1. **解耦几何体**: 确保 `HotspotAnalyzer` 返回原生的 Python 类型（表示边界框的浮点数列表），而不是 `ee.Geometry` 对象。这使得分析模块独立于 GEE 库。
2. **Dask 分块策略**: 在 HPC 脚本中，在将 `xarray.Dataset` 传递给 `HotspotAnalyzer` 并保存到 Zarr 之前，明确定义它的分块策略。例如，`ds = ds.chunk({'lat': 1000, 'lon': 1000})`。
3. **GEEFetcher 中的速率限制**: 在 `GEEFetcher.batch_fetch_hotspots` 中实现延迟或批处理机制，以避免超出 GEE API 限制（例如，分批提交 10 个任务并短暂休眠）。
4. **脚本中的弹性**: `scripts/run_hotspot_ensemble.py` 应实现一种机制来检查 Zarr 输出是否已经存在（或部分存在），以支持恢复失败的 HPC 任务。