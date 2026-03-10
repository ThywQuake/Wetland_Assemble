# GEMINI.md - Wetland Analysis & Ensemble Framework (30m)

## Project Overview
This project is a sophisticated Python framework designed for the integration, consistency analysis, and remote sensing validation of high-resolution (30m) global and regional wetland datasets. It supports heterogeneous data sources (NetCDF, GeoTIFF) and integrates 2026-era Google Earth Engine (GEE) workflows.

### Main Technologies
- **Data Processing**: `xarray`, `rioxarray`, `numpy`, `pandas`, `dask`
- **Geospatial Tools**: `geopandas`, `rasterio`, `pyproj`, `shapely`, `cartopy`
- **Visualization**: `matplotlib`, `seaborn`, `geemap`, `ipyleaflet`
- **Machine Learning/Stats**: `scikit-learn`, `scipy`, `pymannkendall` (implied)
- **Data Integration**: Google Earth Engine (GEE) via `geemap` and `ee`
- **Environment Management**: `uv`, `hatchling` (build backend)

### Architecture
The project follows a standard scientific engineering layout:
- `src/wetland_analysis/`: Core algorithmic library.
  - `analysis/`: Consensus calculation, uncertainty assessment (Shannon Entropy), and trend analysis.
  - `data/`: Data loading (`loader.py`), GEE integration (`satellite_fetcher.py`), and config parsing.
  - `utils/`: MGRS tiling system (optimized for GWD30 15m offset) and spatial resampling.
  - `visualization/`: Publication-quality mapping and interactive notebook widgets.
- `config/`: Centralized dataset configuration (`datasets.yaml`).
- `notebooks/`: Guided exploratory analysis workflows (01-04).
- `tests/`: Automated unit tests using `pytest`.

## Building and Running

### Key Commands
- **Install Dependencies**: `pip install .` or `uv sync` (if using uv).
- **Run Analysis Workflow**: `python -m wetland_analysis` (entry point in `__main__.py`).
- **Run Verification Script**: `python scripts/verify_workflow.py`.
- **Run Tests**: `pytest tests/`.
- **Development Mode**: `pip install -e ".[dev]"`.

### Remote Access
For running notebooks on a remote server, follow the port forwarding instructions in `docs/guides/notebook-setup.md`.

## Development Conventions

### Coding Style
- **Python Standard**: Python 3.10+ with modern type hints (e.g., `list[str]`, `str | None`).
- **Formatting**: Strictly follow `black` and `isort` as configured in `pyproject.toml`.
- **Naming**: Use `snake_case` for variables/functions, `UPPER_SNAKE_CASE` for constants, and `kebab-case` for file names.

### Documentation Standards
- **File Naming**: `YYYY-MM-DD-[type]-[description].md`.
- **Title Hierarchy**: Level 1 for main titles, Level 2 (Chinese numerals: 一、二) for main sections, Level 3 (Arabic: 1.1) for subsections.
- **Color Codes**: Always use 6-digit hex codes (e.g., `#2E7D32`).
- **Tables**: Must include titles and consistent numbering (Table X.X).

### Testing Practices
- **Framework**: `pytest`.
- **Coverage**: Aim for high coverage in `analysis/` and `utils/` modules.
- **Validation**: Always reproduction of remote sensing truth using `Cloud Score+` via GEE.

## Key Files & Purpose
- `pyproject.toml`: Dependency management and tool configuration.
- `config/datasets.yaml`: Centralized registry for all wetland datasets (GWD30, GIEMS-MC, etc.) and analysis regions.
- `src/wetland_analysis/utils/mgrs_tiling.py`: Specialized tiling system for GWD30's 109.83km tiles.
- `docs/guides/style-guide.md`: Comprehensive styling and documentation mandates.
- `GEMINI.md`: (This file) Instructional context for AI agents.
