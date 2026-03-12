# 2026-03-11 Refactor Tailored Dataset Loaders Todo List

- [x] Update `config/datasets.yaml` based on folder structure
- [x] Implement Loader Factory/Registry in `src/wetland_analysis/data/loader.py`
- [x] Implement `GWD30Loader` for ROI-based mosaicking
- [x] Implement `GLWDLoader` for area (ha) and percentage (pct) extraction and scaling
- [x] Implement `TOPMODELLoader` with config and forcing arguments
- [x] Implement `SWAMPSLoader` with time/sensor resolution
- [x] Implement `BerkeleyLoader` to parse dates from file paths
- [x] Update `config.py` validations to support new yaml schema
- [x] Ensure all loaders return standardised `lat`/`lon` coordinates
- [ ] Write integration test verifying dataset loaders resolve correctly