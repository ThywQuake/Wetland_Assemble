---
title: Wetland Dataset Quality Comparison Plan
type: feat
status: active
date: 2026-03-09
origin: docs/brainstorms/2026-03-04-wetland-dataset-evaluation-brainstorm.md
---

# Wetland Dataset Quality Comparison Plan

## Overview
This plan outlines a systematic approach to evaluate and compare the quality of multiple global wetland datasets. We will categorize datasets by their characteristics and apply tailored comparison methods, leveraging high-resolution reference data and existing analysis tools in the codebase.

## Dataset Categorization

Based on `docs/datasets/`, the datasets are categorized as follows:

| Category | Datasets | Resolution | Type | Focus |
| :--- | :--- | :--- | :--- | :--- |
| **High-Res Reference** | GWD30, Sentinel-2 | 30m | Dynamic/Class | Local validation |
| **Medium-Res Static** | G2017, GLWD v2 | 232m - 500m | Static/Class | Tropical/Global baseline |
| **Coarse Dynamic (Frac)**| GIEMS-MC, SWAMPS, TOPMODEL, WAD2M | 0.25° (~25km) | Dynamic/Fraction | Global hydrology |
| **Coarse Dynamic (Mask)**| Berkeley-RWAWC (CYGNSS) | 0.01° (~1km) | Dynamic/Mask | Tropical hydrology |

## Comparison Strategy

### 1. Harmonization & Preprocessing
To enable direct comparison, datasets must be harmonized:
- **Spatial Alignment**: Resample all datasets to common grids:
  - 30m for high-res local comparisons.
  - 0.01° for regional tropical analysis.
  - 0.25° for global trend analysis.
- **Classification Mapping**: Map diverse classification schemes (e.g., GLWD's 33 classes vs GWD30's 14 classes) to a unified **Consensus Wetland Category** (e.g., Forested Wetland, Non-forested Wetland, Open Water).
- **Binary Conversion**: Create "Wetland vs. Non-wetland" masks for overall accuracy assessment across all products.

### 2. Specific Comparison Methods

#### A. Classification Accuracy (vs. High-Res Reference)
**Datasets**: GWD30, G2017, GLWD v2.
**Methods**:
- **Confusion Matrix**: Calculate OA, PA, UA, and Kappa coefficient.
- **Spatial Accuracy**: Use `calculate_spatial_accuracy` from `src/wetland_analysis/analysis/accuracy.py`.
- **Class-Specific Analysis**: Evaluate accuracy for specific types (e.g., Mangroves in G2017 vs. GWD30).

#### B. Dynamic Fraction Accuracy (vs. Aggregated Reference)
**Datasets**: GIEMS-MC, SWAMPS, WAD2M, TOPMODEL.
**Methods**:
- **Aggregation**: Aggregate 30m GWD30 data to 0.25° fractions.
- **Statistical Correlation**: Calculate Pearson and Spearman correlation coefficients.
- **Error Analysis**: Calculate RMSE and Bias (`compare_datasets` in `src/wetland_analysis/analysis/comparison.py`).

#### C. Temporal Trend Consistency
**Datasets**: All dynamic products (GWD30, GIEMS-MC, Berkeley-RWAWC, etc.).
**Methods**:
- **Mann-Kendall Test**: Detect significant trends in wetland extent.
- **Sen's Slope**: Compare the magnitude of change over time.
- **Trend Synchronization**: Evaluate if datasets capture the same seasonal peaks and inter-annual anomalies.

#### D. Uncertainty and Agreement Mapping
- **Consensus Mapping**: Identify areas where multiple datasets agree/disagree.
- **Entropy Analysis**: Use `calculate_entropy` from `src/wetland_analysis/analysis/uncertainty.py` to map hotspots of disagreement.

## Reference Data Acquisition (Sentinel-2)

Since local high-resolution reference data is missing, we must acquire specific Sentinel-2 tiles to serve as the "ground truth" for validation.

### 1. Data Specifications
- **Product Level**: **Sentinel-2 Level-2A (L2A)** (Bottom-of-Atmosphere reflectance).
- **Resolution**: 10m (Visible/NIR) and 20m (SWIR).
- **Core Bands**: 
  - **10m**: B2 (Blue), B3 (Green), B4 (Red), B8 (NIR) for NDVI and visualization.
  - **20m**: B11, B12 (SWIR) for water/moisture detection (mNDWI).
- **Sampling Strategy**: 
  - **Wet Season Peak**: To capture maximum inundation extent.
  - **Dry Season**: To distinguish permanent vs. seasonal wetlands.

### 2. Spatio-Temporal Scope
- **Time Range**: **2018 - 2022** (optimal overlap with GWD30, Berkeley-RWAWC, and GIEMS-MC).
- **Priority Reference Sites**:
  - **Amazon Basin**: Tropical rainforest and large floodplains.
  - **Congo Basin**: Tropical peatlands and swamp forests.
  - **SE Asia Mangroves**: Coastal wetland validation (vs. G2017/GWD30).
  - **Pantanal**: Dynamic trend consistency validation.

## Implementation Phases

### Phase 1: Data Acquisition & Harmonization
- **Sentinel-2 Retrieval**: Use Google Earth Engine (GEE) or Sentinel Hub to export median composites for priority sites (Dry/Wet seasons).
- **Mapping Scripts**: Implement cross-walk tables for GLWD v2 and GWD30 classification schemes.
- **Tiling System**: Setup MGRS-based tiling for high-res comparison (see `src/wetland_analysis/utils/mgrs_tiling.py`).
- **Standardization**: Resample acquired Sentinel-2 data to 10m/30m grids for direct comparison with GWD30.

### Phase 2: Static Baseline Comparison
- Compare GLWD v2 and G2017 in the pantropical belt.
- Validate static products against a 10-year average of GWD30.
- Generate spatial agreement maps.

### Phase 3: Dynamic & Trend Analysis
- Perform monthly correlation analysis between coarse fraction products.
- Compare Berkeley-RWAWC (CYGNSS) against GIEMS-MC and GWD30 in the tropics.
- Execute Mann-Kendall trend analysis across all dynamic products for 2013-2022 (overlap period).

### Phase 4: Reporting & Visualization
- Generate automated Markdown reports with `src/wetland_analysis/visualization/reports.py`.
- Create spatial maps showing "Best Dataset per Region" based on reference validation.

## Acceptance Criteria
- [ ] Cross-walk table for all classification schemes is defined.
- [ ] Spatial accuracy metrics (OA, Kappa) are calculated for all class-based products.
- [ ] Temporal correlation maps are generated for all dynamic products.
- [ ] Trend consistency (Sen's Slope) is evaluated for the 2013-2022 period.
- [ ] An "Uncertainty Hotspot" map is produced showing areas of maximum disagreement.

## Sources
- **Origin Brainstorm**: `docs/brainstorms/2026-03-04-wetland-dataset-evaluation-brainstorm.md`
- **Dataset Docs**: `docs/datasets/*.md`
- **Analysis Tools**: `src/wetland_analysis/analysis/`
