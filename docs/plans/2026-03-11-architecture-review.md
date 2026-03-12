# Architecture Review: Hotspot GEE Extraction (Deepened Plan)

## 1. Architecture Overview
The current system architecture is a Python-based scientific pipeline (`WetlandEnsemblePipeline`) designed to ingest multiple wetland datasets, align them temporally and spatially (`SpatioTemporalAligner`), and produce consensus and uncertainty (Shannon Entropy) maps using `xarray`. There is an independent `GEEFetcher` component responsible for authenticating with Google Earth Engine (GEE) and fetching Sentinel-2 composites. The new plan introduces `HotspotAnalyzer` to bridge these two: identifying high-uncertainty regions from the pipeline's output and triggering GEE data extraction via a new `batch_fetch_hotspots` method in `GEEFetcher`. The plan also shifts the execution environment from interactive Notebooks to a headless HPC environment using Dask (`dask-jobqueue`/`dask-mpi`).

## 2. Change Assessment
The proposed changes fit naturally into the existing pipeline.
- `HotspotAnalyzer` acts as a downstream consumer of the `WetlandEnsemblePipeline`'s output (`run_analysis()` returning an `xr.Dataset` with `shannon_entropy`).
- `GEEFetcher` is being appropriately extended (`batch_fetch_hotspots`) to support the new batch-oriented workflow rather than just single-image extraction (`get_sentinel2_image`).
- The transition to HPC via `scripts/run_hotspot_ensemble.py` is a standard evolution for scientific pipelines scaling up.

## 3. Compliance Check
- **Single Responsibility Principle (SRP):** Upheld. `HotspotAnalyzer` focuses solely on finding hotspots. `GEEFetcher` handles GEE interaction. The main script coordinates them.
- **Separation of Concerns:** Well maintained. The pipeline generates the data, the analyzer interprets the data, and the script handles the infrastructure (Dask/HPC).
- **Dependency Inversion:** The plan doesn't explicitly mention interfaces, but keeping `HotspotAnalyzer` decoupled from the internal workings of `GEEFetcher` (passing generic bounds/coordinates) will be crucial.

## 4. Risk Analysis
- **Coupling Risk:** There is a risk of coupling `HotspotAnalyzer` too tightly to GEE's specific coordinate requirements (`ee.Geometry`). `HotspotAnalyzer` should output standard WGS84 bounding boxes (e.g., `[(min_lon, min_lat, max_lon, max_lat), ...]`), and `GEEFetcher` should be responsible for translating these into `ee.Geometry.Rectangle`.
- **Dask/Xarray Integration:** Using `dask.array` for the sliding window in `HotspotAnalyzer` is technically challenging. Standard `xarray.rolling` operations can be memory-intensive even with Dask. Depending on the window size and the chunking strategy of the input Zarr file, this could lead to Dask worker memory blowouts.
- **GEE Rate Limits:** The new `batch_fetch_hotspots` could easily hit GEE concurrent task or query limits if not implemented with appropriate throttling or batching strategies.
- **Data Persistence:** The plan mentions saving to Zarr, but ensuring the intermediate steps (alignment -> entropy) are correctly chunked before saving is critical for the downstream `HotspotAnalyzer` performance.

## 5. Recommendations
1. **Decouple Geometry:** Ensure `HotspotAnalyzer` returns native Python types (lists of floats representing bounding boxes) rather than `ee.Geometry` objects. This keeps the analysis module independent of the GEE library.
2. **Dask Chunking Strategy:** In the HPC script, explicitly define a chunking strategy for the `xarray.Dataset` before passing it to the `HotspotAnalyzer` and before saving to Zarr. E.g., `ds = ds.chunk({'lat': 1000, 'lon': 1000})`.
3. **Rate Limiting in GEEFetcher:** Implement a delay or batching mechanism in `GEEFetcher.batch_fetch_hotspots` to avoid exceeding GEE API limits (e.g., submitting tasks in batches of 10 with a short sleep).
4. **Resilience in Script:** The `scripts/run_hotspot_ensemble.py` should implement a mechanism to check if the Zarr output already exists (or partially exists) to support resuming failed HPC jobs.