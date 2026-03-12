---
title: "feat: GWD30 严谨坐标转换与瓦片系统实现"
type: feat
status: active
date: 2026-03-05
---

# feat: GWD30 严谨坐标转换与瓦片系统实现

## Overview

针对 GWD30 数据集的特殊瓦片设计（基于 MGRS 但带有 15m 偏移量及 109.83km 扩展），开发一套严谨的坐标转换工具。该工具将支持代号与坐标范围互转、单点代号检索以及区域覆盖瓦片计算，为后续的大规模并行处理与数据检索提供基础。

## Problem Statement / Motivation

GWD30 数据集具有以下特殊性，导致标准 MGRS 库无法直接使用：
1. **偏移修正**：为了对齐 Landsat 和 Sentinel-2，标准 MGRS 网格在 X/Y 方向偏移了 15m。
2. **瓦片尺寸**：标准 MGRS 瓦片通常为 100km，而 GWD30 扩展到了 109.83km（3661 像素）。
3. **检索需求**：在分析特定地理区域时，需要快速确定需要加载哪些 `.tif` 文件。

## Proposed Solution

在 `src/wetland_analysis/utils/geospatial.py` 中（或新开 `mgrs_tiling.py`）实现一个专用的瓦片管理器。

### 核心逻辑设计

1. **投影转换**: 利用 `pyproj` 动态生成 UTM 坐标系 (EPSG:326xx 或 327xx)。
2. **代号解析**: 解析如 `50TMK` 的 MGRS 字符串。
3. **坐标校准**:
   - $X_{GWD30} = X_{MGRS} - 15$
   - $Y_{GWD30} = Y_{MGRS} - 15$
   - $Size = 109,830 \text{ meters}$
4. **范围查询**: 使用 `shapely` 进行几何相交判定，快速筛选 ROI 覆盖的瓦片代号。

## Technical Considerations

- **性能**: 范围查询可能涉及大量瓦片，需要预计算或使用高效的索引。
- **极地支持**: MGRS 在南北极（UPS 投影）有特殊处理，需确认 GWD30 是否覆盖及如何处理。
- **依赖**: 优先使用已有库 `pyproj`, `shapely`, `numpy`。

## System-Wide Impact

- **数据检索**: `loader_tools.py` 将调用此模块进行文件过滤。
- **预处理**: 自动根据瓦片边界切分大范围数据。

## Acceptance Criteria

- [ ] 实现 `GWD30TilingSystem` 类。
- [ ] `tile_to_extent(tile_code)`: 返回经纬度范围 `(W, S, E, N)`。
- [ ] `point_to_tile(lat, lon)`: 返回该点所属的瓦片代号。
- [ ] `bbox_to_tiles(bbox)`: 返回给定矩形区域内包含的所有瓦片代号列表。
- [ ] 误差验证：转换误差应小于 1 米（考虑到投影转换精度）。
- [ ] 提供单元测试，覆盖跨 UTM 带、赤道等边缘情况。

## MVP Code Structure (Pseudo)

### `src/wetland_analysis/utils/mgrs_tiling.py`

```python
import pyproj
from shapely.geometry import box, Point
import numpy as np

class GWD30TilingSystem:
    def __init__(self, offset_x=-15, offset_y=-15, tile_size=109830):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.tile_size = tile_size

    def get_tile_bbox(self, tile_code: str):
        # 1. Parse MGRS to UTM coords
        # 2. Apply offsets
        # 3. Project back to WGS84 for extent
        pass

    def get_tiles_for_region(self, min_lat, min_lon, max_lat, max_lon):
        # Return list of tile codes
        pass
```

## Sources & References

- **GWD30 Metadata:** `infos/GWD30.md`
- **MGRS Standard:** Military Grid Reference System documentation.
- **Reference Article:** Claverie et al. (2018) for HLS alignment logic.
