---
title: 具体化湿地数据集对比方案实施细节
type: feat
status: active
date: 2026-03-10
origin: docs/plans/2026-03-09-feat-wetland-dataset-comparison-zh-plan-deepened.md
---

# 湿地数据集对比方案具体化实施细节

## 概述
本方案旨在将“深度增强版”计划转化为具体、可执行的技术规范。我们将详细定义分类映射字典、空间对齐算法、具体对比样区坐标以及调用 `src/wetland_analysis/` 模块的伪代码逻辑。

## 1. 核心任务：分类体系映射 (Classification Cross-walk)

不同数据集（GLWD, GWD30, G2017）的类别定义迥异。为实现对比，必须统一映射为“共识湿地类别”。

### 映射字典定义
我们将定义一个核心映射逻辑，将所有类别归并为：
- **0: Non-wetland (非湿地)**
- **1: Permanent Water (永久性水体)**
- **2: Forested Wetland (有林湿地/沼泽)**
- **3: Non-forested Wetland (无林湿地/草本湿地)**

#### 映射示例 (GLWD v2 -> Consensus):
- GLWD 01-07 -> 1 (Water)
- GLWD 08, 10, 12, 14, 16, 18, 22, 24, 26, 28 -> 2 (Forested)
- GLWD 09, 11, 13, 15, 17, 19, 23, 25, 27, 29 -> 3 (Non-forested)

## 2. 空间对齐与重采样规范

- **高分辨率验证 (30m)**:
  - 参考网格: GWD30 30m Grid.
  - 算法: 针对分类图 (Categorical) 使用 `mode` (众数)；针对概率图 (Continuous) 使用 `bilinear`。
- **全球趋势分析 (0.25°)**:
  - 参考网格: WAD2M/GIEMS-MC 0.25° Grid.
  - 算法: 面积加权平均 (Area-weighted averaging)，计算每个 25km 网格内的湿地面积百分比。

## 3. 具体对比样区 (Reference Sites)

基于 `config/datasets.yaml` 的热带/亚热带重心，选定以下 4 个 1° x 1° 的核心样区：

| 样区名称 | 经纬度范围 (min_lon, min_lat, max_lon, max_lat) | 湿地特征 |
| :--- | :--- | :--- |
| **Amazon_Central** | [-65.0, -3.0, -64.0, -2.0] | 热带森林湿地、大型河漫滩 |
| **Congo_Peat** | [17.5, -0.5, 18.5, 0.5] | 典型热带泥炭地 (Cuvette Centrale) |
| **SE_Asia_Mangrove** | [103.5, 1.2, 104.5, 2.2] | 红树林、滨海湿地 (新加坡/马来西亚周边) |
| **Pantanal_Dynamic** | [-57.0, -19.0, -56.0, -18.0] | 强动态季节性草本湿地 |

## 4. 技术实现路径 (MVP 伪代码)

### 4.1 数据加载与统一映射
```python
# src/wetland_analysis/data/preprocessing.py
def harmonize_classes(data, source_type='GLWD'):
    mapping = {
        'GLWD': {range(1, 8): 1, (8, 10, 12): 2, (9, 11, 13): 3},
        'GWD30': {range(1, 8): 1, (9, 12): 2, (8, 11): 3}
    }
    # 应用映射逻辑生成统一分类图
    return data.map_blocks(apply_mapping, args=(mapping[source_type],))
```

### 4.2 精度验证执行
```python
# 调用现有模块进行精度计算
from wetland_analysis.analysis.accuracy import calculate_spatial_accuracy

results = calculate_spatial_accuracy(
    reference=gwd30_mapped,
    target=glwd_mapped,
    classes=[1, 2, 3],
    class_names=['Water', 'Forested', 'Non-forested']
)
# 输出 OA, Kappa, 以及各类别 PA/UA
```

### 4.3 趋势分析配置
- **参数**: `alpha=0.05` (显著性水平).
- **分块**: `chunks={'time': -1, 'lat': 500, 'lon': 500}`.
- **输出**: 显著增加区域、显著减少区域、无显著变化区域。

## 5. 验收标准
- [ ] 导出 `mappings.json` 文件，包含所有 8 个数据集的分类映射规则。
- [ ] 自动化脚本支持批量计算 4 个样区的混淆矩阵。
- [ ] 生成包含 4 个样区精度对比的 Markdown 汇总报告 (`reports/comparison_summary.md`)。
- [ ] 样区对比图中必须包含 Sentinel-2 (L2A) 作为底层背景图。

## 6. 来源与参考
- **源计划**: [docs/plans/2026-03-09-feat-wetland-dataset-comparison-zh-plan-deepened.md](docs/plans/2026-03-09-feat-wetland-dataset-comparison-zh-plan-deepened.md)
- **代码实现**: `src/wetland_analysis/analysis/accuracy.py`
- **配置文件**: `config/datasets.yaml`
