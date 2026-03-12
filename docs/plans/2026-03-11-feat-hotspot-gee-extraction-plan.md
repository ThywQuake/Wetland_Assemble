---
title: "feat: Hotspot GEE Extraction & Ensemble Pipeline Integration"
type: feat
status: active
date: 2026-03-11
origin: docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md
---

# feat: Hotspot GEE Extraction & Ensemble Pipeline Integration

## Overview
This feature integrates the `WetlandEnsemblePipeline` with `GEEFetcher` to automate the discovery and remote sensing validation of "Hotspots" — areas where global wetland datasets exhibit maximum disagreement (high Shannon Entropy).

## Problem Statement / Motivation
Currently, identifying where datasets disagree requires manual inspection. To validate the "truth" in these high-uncertainty zones, we need a streamlined flow that:
1. Calculates spatial uncertainty across a study region.
2. Identifies specific bounding boxes with the highest conflict.
3. Automatically fetches high-resolution (Sentinel-2) imagery via GEE for visual or algorithmic refinement.

## Proposed Solution
Introduce a `HotspotAnalyzer` utility and a dedicated Jupyter Notebook (`05_hotspot_gee_extraction.ipynb`) that orchestrates the end-to-end flow.

### 1. Hotspot Identification Logic
- Develop `src/wetland_analysis/analysis/hotspots.py` to extract ROI candidates from entropy maps.
- Implement a clustering or "Top-N Window" search to find 100km x 100km (or smaller) areas with peak disagreement.

### 2. GEE Connector
- Link `HotspotAnalyzer` outputs directly to `GEEFetcher.get_sentinel2_image`.
- Ensure `GEEFetcher` handles WGS84 bounding boxes correctly for Sentinel-2 Cloud Score+ composites.

### 3. Interactive Verification
- Create `notebooks/05_hotspot_gee_extraction.ipynb` for manual execution as requested.

## Technical Considerations
- **Memory Efficiency**: Use `xarray` with Dask to handle large regions before cropping to hotspots.
- **Coordinate Systems**: Ensure correct transformation between `xarray` (lat/lon) and `ee.Geometry.Rectangle`.
- **GEE Authentication**: Use the newly established `gee_config.yaml` for zero-setup initialization.

## System-Wide Impact
- **Interaction graph**: `Pipeline` -> `HotspotAnalyzer` -> `GEEFetcher` -> `Verification Notebook`.
- **Error propagation**: Handle GEE timeout or "no imagery found" errors gracefully within the notebook.
- **API surface parity**: Ensure `GEEFetcher` remains usable as a standalone tool while supporting pipeline-driven queries.

## Acceptance Criteria
- [ ] `HotspotAnalyzer` can identify Top-N regions from an `xarray` entropy map.
- [ ] `GEEFetcher` successfully initializes using `config/gee_config.yaml`.
- [ ] `notebooks/05_hotspot_gee_extraction.ipynb` runs successfully from start to finish.
- [ ] Visualization in the notebook shows:
    - Consensus map.
    - Uncertainty (Entropy) map.
    - Sentinel-2 true-color composite for at least one hotspot.

## MVP Files to Create/Modify
- `src/wetland_analysis/analysis/hotspots.py` (New)
- `notebooks/05_hotspot_gee_extraction.ipynb` (New)
- `src/wetland_analysis/analysis/__init__.py` (Export new analyzer)

## Sources & References
- **Origin brainstorm:** [docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md](docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md)
- **Tiling Logic:** [src/wetland_analysis/utils/mgrs_tiling.py](src/wetland_analysis/utils/mgrs_tiling.py)
- **GEE Integration:** [src/wetland_analysis/data/satellite_fetcher.py](src/wetland_analysis/data/satellite_fetcher.py)
