"""
Dataset loader for wetland datasets.
"""

import xarray as xr
import rasterio
import rioxarray
import geopandas as gpd
import numpy as np
import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import logging

logger = logging.getLogger(__name__)

# Load dataset configuration
_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "datasets.yaml"


def load_dataset_config() -> Dict:
    """Load dataset configuration from YAML file."""
    if not _CONFIG_PATH.exists():
        raise FileNotFoundError(f"Dataset configuration not found at {_CONFIG_PATH}")

    with open(_CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)

    return config


def list_available_datasets() -> List[str]:
    """List all available wetland datasets from configuration."""
    config = load_dataset_config()
    return list(config.get('datasets', {}).keys())


def get_dataset_info(dataset_name: str) -> Dict:
    """Get configuration information for a specific dataset."""
    config = load_dataset_config()
    datasets = config.get('datasets', {})

    if dataset_name not in datasets:
        available = list(datasets.keys())
        raise ValueError(f"Dataset '{dataset_name}' not found. Available datasets: {available}")

    return datasets[dataset_name]


def load_wetland_dataset(
    dataset_name: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    region: Optional[str] = None,
    variables: Optional[List[str]] = None
) -> Union[xr.Dataset, xr.DataArray]:
    """
    Load a wetland dataset.

    Parameters
    ----------
    dataset_name : str
        Name of the dataset (e.g., 'gwd30', 'giems_mc')
    year : int, optional
        Year for time-series datasets
    month : int, optional
        Month for monthly datasets
    region : str, optional
        Region name from configuration
    variables : list of str, optional
        Specific variables to load

    Returns
    -------
    xr.Dataset or xr.DataArray
        Loaded dataset
    """
    dataset_info = get_dataset_info(dataset_name)
    data_format = dataset_info.get('format', '').lower()

    # Get dataset path (user needs to update config with actual paths)
    base_path = dataset_info.get('path', '')
    if base_path == '/path/to/data/':
        raise ValueError(
            f"Dataset path not configured for {dataset_name}. "
            f"Please update {_CONFIG_PATH} with actual data paths."
        )

    if data_format == 'netcdf':
        return _load_netcdf_dataset(dataset_info, year, month, variables)
    elif data_format == 'geotiff':
        return _load_geotiff_dataset(dataset_info, year, month)
    else:
        raise ValueError(f"Unsupported format: {data_format}")


def _load_netcdf_dataset(
    dataset_info: Dict,
    year: Optional[int] = None,
    month: Optional[int] = None,
    variables: Optional[List[str]] = None
) -> xr.Dataset:
    """Load NetCDF dataset."""
    base_path = dataset_info['path']

    # Handle different NetCDF file patterns
    if 'file' in dataset_info:
        # Single file dataset
        file_path = Path(base_path) / dataset_info['file']
        ds = xr.open_dataset(file_path)
    elif 'pattern' in dataset_info:
        # Multiple files with pattern
        pattern = dataset_info['pattern']
        if year and month:
            # Replace placeholders in pattern
            pattern = pattern.replace('{year}', str(year))
            pattern = pattern.replace('{month}', f'{month:02d}')
        elif year:
            pattern = pattern.replace('{year}', str(year))

        file_path = Path(base_path) / pattern
        ds = xr.open_mfdataset(str(file_path), combine='by_coords')
    else:
        raise ValueError("NetCDF dataset configuration must include 'file' or 'pattern'")

    # Select specific variables if requested
    if variables:
        available_vars = list(ds.data_vars)
        missing = [v for v in variables if v not in available_vars]
        if missing:
            logger.warning(f"Variables not found: {missing}")
        ds = ds[variables]

    return ds


def _load_geotiff_dataset(
    dataset_info: Dict,
    year: Optional[int] = None,
    month: Optional[int] = None
) -> xr.DataArray:
    """Load GeoTIFF dataset."""
    base_path = dataset_info['path']

    # Handle different GeoTIFF file patterns
    if 'files' in dataset_info:
        # Multiple files defined
        if 'wetland' in dataset_info['files']:
            file_path = Path(base_path) / dataset_info['files']['wetland']
        else:
            # Use first available file
            first_file = list(dataset_info['files'].values())[0]
            file_path = Path(base_path) / first_file
    elif 'pattern' in dataset_info:
        # Pattern-based files
        pattern = dataset_info['pattern']
        if year:
            pattern = pattern.replace('{year}', str(year))
        file_path = Path(base_path) / pattern
    else:
        raise ValueError("GeoTIFF dataset configuration must include 'files' or 'pattern'")

    # Use rioxarray to open GeoTIFF
    da = rioxarray.open_rasterio(file_path)

    # Squeeze band dimension if it's 1
    if da.shape[0] == 1:
        da = da.squeeze('band')

    return da


def validate_dataset_loaded(
    data: Union[xr.Dataset, xr.DataArray],
    dataset_name: str
) -> bool:
    """Validate that dataset was loaded correctly."""
    if isinstance(data, xr.Dataset):
        if len(data.data_vars) == 0:
            logger.error(f"Dataset {dataset_name} loaded but contains no data variables")
            return False
    elif isinstance(data, xr.DataArray):
        if data.size == 0:
            logger.error(f"DataArray {dataset_name} loaded but is empty")
            return False
    else:
        logger.error(f"Unknown data type for {dataset_name}: {type(data)}")
        return False

    logger.info(f"Successfully loaded dataset: {dataset_name}")
    return True