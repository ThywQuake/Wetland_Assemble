---
title: 湿地数据集分类精度与动态趋势评估系统
type: feat
status: active
date: 2026-03-04
origin: docs/brainstorms/2026-03-04-wetland-dataset-evaluation-brainstorm.md
---

# 湿地数据集分类精度与动态趋势评估系统

## Overview

构建一个评估框架系统，用于对全球湿地卫星数据集进行分类精度评价和动态趋势准确度评估。该系统支持：
- 空间分布一致性评估（基于高分辨率卫星数据作为参考）
- 动态趋势一致性评估（时间序列趋势分析）
- 混合验证方法（参考数据 + 数据集间互相对比）

## Problem Statement

当前湿地数据集（如GIEMS-MC, WAD2M, SWAMPS, GWD30等）缺乏系统性的精度评估和跨数据集比较机制。不同数据集的分辨率（30m ~ 27km）、分类类型（类别型 vs 分数型）和时间范围差异使得难以：
1. 确定各数据集的可靠性
2. 识别数据集间的系统性偏差
3. 验证动态趋势的准确性

## Proposed Solution

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Evaluation Framework                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Data Loader │  │ Preprocess │  │  Evaluator  │              │
│  │  Module     │  │   Module   │  │   Module    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Report Generator (Markdown)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation Phases

#### Phase 1: 核心评估模块

**任务 1.1: 数据加载器**
- 实现数据集配置文件读取（YAML/JSON）
- 支持NetCDF, GeoTIFF, CSV格式
- 支持时间序列数据

**任务 1.2: 空间对齐预处理**
- 统一坐标参考系（EPSG:4326）
- 分辨率重采样（最近邻、双线性、众数）
- 分类模式转换：类别型 ↔ 二值型

**任务 1.3: 分类精度计算**
- 混淆矩阵生成
- OA, Kappa, PA, UA, F1-Score计算
- 置信区间估计

#### Phase 2: 趋势分析模块

**任务 2.1: 时间序列处理**
- 月度/年度聚合
- 缺失值处理（线性插值）
- 季节性分解（可选）

**任务 2.2: 趋势检验**
- Mann-Kendall趋势检验
- Sen's Slope斜率估计
- 相关性分析（Pearson/Spearman）

**任务 2.3: 跨数据集趋势比较**
- 趋势方向一致性分析
- 趋势幅度差异比较

#### Phase 3: 可视化与报告

**任务 3.1: 统计图表生成**
- 精度指标条形图
- Kappa分布热力图
- 相关性矩阵

**任务 3.2: 空间分布图**
- 湿地分布对比图
- 差异空间图
- 多数据集叠加可视化

**任务 3.3: 趋势变化图**
- 时间序列折线图
- Sen's Slope空间分布图

**任务 3.4: Markdown报告生成**
- 自动生成评估报告
- 包含所有指标和可视化链接

## Technical Approach

### 数据预处理决策

| 问题 | 解决方案 |
|------|----------|
| 分辨率差异（30m vs 27km） | 降采样使用众数（类别型）/ 均值（分数型）；升采样使用双线性 |
| 分类模式差异 | 统一转换为二值型（湿地/非湿地），GIEMS-MC使用阈值0.1 |
| 时间粒度差异 | 统一到年度聚合（支持月度可选） |
| 时间范围重叠 | 取重叠时期，GIEMS-MC(1992-2020)与GWD30(2013-2024)取2013-2020 |

### 评估指标规范

**分类精度指标：**
| 指标 | 公式/方法 | 阈值 |
|------|-----------|------|
| Overall Accuracy | (TP+TN)/(TP+TN+FP+FN) | >85% |
| Kappa | (Po-Pe)/(1-Pe) | >0.70 |
| Producer's Accuracy | TP/(TP+FN) | >80% |
| User's Accuracy | TP/(TP+FP) | >80% |
| F1-Score | 2*Precision*Recall/(Precision+Recall) | >0.80 |

**趋势准确度指标：**
| 指标 | 方法 | 参数 |
|------|------|------|
| 趋势相关性 | Pearson Correlation | r>0.7 |
| 趋势显著性 | Mann-Kendall | p<0.05 |
| 趋势幅度 | Sen's Slope | 报告CI |
| 趋势一致性 | 方向匹配率 | >80% |

### 参考数据源

| 数据源 | 分辨率 | 时间范围 | 用途 |
|--------|--------|----------|------|
| Sentinel-2 | 10-20m | 2015-现在 | 高分辨率验证 |
| Landsat | 30m | 1984-现在 | 历史验证 |
| GSW | 30m | 1984-2020 | 水体边界验证 |

### 误差处理

| 场景 | 处理方式 |
|------|----------|
| 空值/无数据 | 排除该像素，报告有效样本数 |
| 分辨率差异 | 按上述预处理规范处理 |
| 时间不匹配 | 取最近时间点并标注 |
| 完全无湿地区域 | 跳过该区域，标注为"无可比数据" |
| 处理失败 | 记录错误日志，继续处理其他区域 |

## System-Wide Impact

### 交互图谱

```
用户输入 → 数据加载 → 预处理 → 精度评估 → 趋势分析 → 报告生成
    │                                              │
    └────────────────── 结果输出 ←──────────────────┘
```

### 边界情况

- 数据集时间范围完全不重叠：返回错误，提示无可比较数据
- 参考数据缺失：使用其他可用参考数据，标注数据来源
- 内存限制：分块处理，按地理分区计算

## Acceptance Criteria

### 功能需求

- [ ] 支持加载YAML配置的数据集元信息
- [ ] 实现空间重采样（降采样/升采样）
- [ ] 支持分类模式转换（二值化）
- [ ] 计算混淆矩阵和精度指标
- [ ] 实现Mann-Kendall趋势检验
- [ ] 计算Sen's Slope趋势斜率
- [ ] 支持两两数据集比较
- [ ] 支持选定基准数据集比较
- [ ] 生成统计图表（PNG）
- [ ] 生成空间分布对比图
- [ ] 生成趋势变化折线图
- [ ] 输出Markdown格式评估报告

### 非功能需求

- [ ] 支持热带和亚热带地区评估
- [ ] 支持月度/年度时间粒度
- [ ] 处理时间：单次评估 <5分钟（单数据集 vs 参考）
- [ ] 报告语言：中文为主，关键指标英文缩写

### 质量标准

- [ ] 所有评估指标附带95%置信区间
- [ ] 趋势分析至少10个时间点
- [ ] 采样点数量 ≥500（空间验证）
- [ ] 报告包含数据质量说明

## Dependencies & Risks

### 依赖项

| 依赖 | 版本 | 用途 |
|------|------|------|
| xarray | >=2024.1 | NetCDF处理 |
| rasterio | >=1.3 | GeoTIFF处理 |
| numpy | >=1.24 | 数值计算 |
| scipy | >=1.11 | 统计检验 |
| matplotlib | >=3.8 | 可视化 |
| pandas | >=2.1 | 数据处理 |

### 风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 高分辨率数据获取困难 | 无法验证 | 使用GSW作为备选 |
| 分辨率差异导致偏差 | 精度评估不准 | 明确标注 aggregation 方法 |
| 分类阈值选择敏感 | 结果不确定 | 提供阈值敏感性分析 |

## Resource Requirements

- Python 3.10+
- 8GB+ RAM
- 参考数据存储：~50GB（Sentinel-2/Landsat选取区域）

## Future Considerations

- 支持更多分类类型（不只是二值）
- 集成Google Earth Engine API
- 支持Web界面
- 自动数据下载集成

## Sources & References

### Origin

- **Brainstorm document:** [docs/brainstorms/2026-03-04-wetland-dataset-evaluation-brainstorm.md](docs/brainstorms/2026-03-04-wetland-dataset-evaluation-brainstorm.md)
- Key decisions carried forward:
  - 评估框架为主（非完整流水线）
  - 热带和亚热带地区优先
  - 混合验证模式（高分辨率卫星 + 数据集间对比）
  - Markdown报告输出
  - 全部可视化类型

### External References

- Google Earth Engine Accuracy Assessment: https://github.com/gee-community/geemap/blob/master/docs/notebooks/33_accuracy_assessment.ipynb
- SciPy Kendall Tau: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kendalltau.html
- Copernicus Sentinel-2: https://documentation.dataspace.copernicus.eu

### 关键规范说明

- **分类阈值**: GIEMS-MC等分数型数据使用0.1作为湿地存在阈值（二值化）
- **重采样方法**: 降采样使用众数（类别型）或均值（分数型）；升采样使用双线性
- **趋势分析**: Mann-Kendall检验显著性水平α=0.05
- **采样策略**: 分层随机采样，按湿地概率五分位分层
