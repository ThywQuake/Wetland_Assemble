---
title: "feat: Hotspot GEE Extraction & Ensemble Pipeline Integration (Deepened)"
type: feat
status: active
date: 2026-03-11
origin: docs/brainstorms/2026-03-05-exploratory-notebooks-brainstorm.md
---

# feat: Hotspot GEE Extraction & Ensemble Pipeline Integration (Deepened)

## Overview
This feature integrates the `WetlandEnsemblePipeline` with `GEEFetcher` to automate the discovery and remote sensing validation of "Hotspots" — areas where global wetland datasets exhibit maximum disagreement (high Shannon Entropy). **This version is optimized for high-performance computing (HPC) environments, transitioning from interactive notebooks to robust batch scripts for ultra-large scale processing.**

## Problem Statement / Motivation
Currently, identifying where datasets disagree requires manual inspection. To validate the "truth" in these high-uncertainty zones, we need a streamlined flow that:
1. Calculates spatial uncertainty across a study region at scale.
2. Identifies specific bounding boxes with the highest conflict.
3. Automatically fetches high-resolution (Sentinel-2) imagery via GEE for visual or algorithmic refinement.
4. **Operates reliably on server computing nodes (SLURM/PBS) outside of the Jupyter environment.**

## Proposed Solution
Introduce a `HotspotAnalyzer` utility, a production-ready batch script (`scripts/run_hotspot_ensemble.py`), and a diagnostic Jupyter Notebook for result inspection.

### 1. Hotspot Identification Logic
- **`src/wetland_analysis/analysis/hotspots.py`**:
    - Extract ROI candidates from entropy maps using a sliding window or clustering approach.
    - Implement `find_top_n_hotspots(entropy_da, n=5, window_size=0.1)` (degrees).
    - **Optimization**: Use `dask.array` for parallel window calculations to avoid loading the full global entropy map into memory.

### 2. GEE Connector & Batch Extraction
- Link `HotspotAnalyzer` outputs directly to `GEEFetcher`.
- **`GEEFetcher` Enhancement**: Add `batch_fetch_hotspots(hotspot_list)` to handle multiple exports to Google Drive/Cloud Storage in parallel.
- Ensure GEE authentication uses `config/gee_config.yaml` to avoid interactive login prompts on headless server nodes.

### 3. High-Performance Batch Script
- **`scripts/run_hotspot_ensemble.py`**:
    - **Dask Integration**: Support `dask-jobqueue` (for SLURM/PBS) and `dask-mpi` for seamless scaling to multiple server nodes.
    - **Configuration**: Use CLI arguments (via `argparse`) for ROI, time range, and Dask cluster settings.
    - **Persistence**: Save intermediate results (Entropy, Consensus) as **Zarr** files (optimized for Dask) to allow for job resumption.

## Technical Considerations (HPC & Dask)
- **Memory Management**: 
    - Set Dask memory limits slightly lower than physical RAM to prevent OOM kills on shared nodes.
    - Use `dask.distributed.performance_report` to generate HTML diagnostics for headless runs.
- **Error Handling**:
    - Implement a "Fail-Safe" retry mechanism for GEE requests.
    - Use `logging` instead of `print` to capture logs into server `.out` and `.err` files.
- **Checkpointing**:
    - Save the final `xarray.Dataset` with all aligned sources and metrics to a Zarr store.

## System-Wide Impact
- **Interaction graph**: `run_hotspot_ensemble.py` (CLI) -> `Pipeline` -> `HotspotAnalyzer` -> `GEEFetcher`.
- **API surface parity**: `GEEFetcher` and `Pipeline` can be called from both Notebooks (small ROI) and Scripts (Global/HPC scale).

## Acceptance Criteria
- [x] `HotspotAnalyzer` identifies Top-N regions from a Dask-backed `xarray` entropy map.
- [x] `scripts/run_hotspot_ensemble.py` runs on a SLURM/PBS node without manual intervention.
- [x] Script generates a `dask-report.html` for performance auditing.
- [x] Intermediate and final results are saved to Zarr format.
- [x] At least one Sentinel-2 true-color composite is successfully triggered for export from a headless script.

## MVP Files to Create/Modify
- `src/wetland_analysis/analysis/hotspots.py` (Created)
- `scripts/run_hotspot_ensemble.py` (Created)
- `notebooks/05_hotspot_gee_extraction.ipynb` (Updated for result inspection only)
- `src/wetland_analysis/analysis/__init__.py` (Export new analyzer)

## Sources & References
- **Dask HPC Best Practices**: Use `dask-mpi` for batch scripts and `performance_report` for headless diagnostics.
- **Zarr Documentation**: Use Zarr for distributed writes from multiple Dask workers.
- **GEE Headless Auth**: Service account or pre-configured `gee_config.yaml`.
