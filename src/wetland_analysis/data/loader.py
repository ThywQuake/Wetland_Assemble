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


import xarray as xr
import rasterio
import rioxarray
import geopandas as gpd
import numpy as np
import yaml
import os
import glob
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import logging

logger = logging.getLogger(__name__)

# Standard coordinate names for consistency
COORD_MAP = {
    'latitude': 'lat',
    'longitude': 'lon',
    'Latitude': 'lat',
    'Longitude': 'lon',
    'y': 'lat',
    'x': 'lon'
}

def _standardize_coords(ds: Union[xr.Dataset, xr.DataArray]) -> Union[xr.Dataset, xr.DataArray]:
    """Ensure dimensions are consistently named 'lat' and 'lon'."""
    rename_dict = {old: new for old, new in COORD_MAP.items() if old in ds.dims}
    if rename_dict:
        logger.debug(f"Standardizing coordinates: {rename_dict}")
        ds = ds.rename(rename_dict)
    return ds

def load_wetland_dataset(
    dataset_name: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    variables: Optional[List[str]] = None
) -> Union[xr.Dataset, xr.DataArray]:
    """
    Robustly load a wetland dataset with coordinate standardization and 
    flexible file searching.
    """
    from .config import load_dataset_config
    config = load_dataset_config()
    dataset_info = config['datasets'].get(dataset_name.lower())
    
    if not dataset_info:
        raise ValueError(f"Dataset {dataset_name} not defined in config.")

    data_format = dataset_info.get('format', '').lower()
    base_path = Path(dataset_info['path'])

    if data_format == 'netcdf':
        data = _load_netcdf_robust(base_path, dataset_info, year, month, variables)
    elif data_format == 'geotiff':
        data = _load_geotiff_robust(base_path, dataset_info, year, month)
    else:
        raise ValueError(f"Unsupported format: {data_format}")

    return _standardize_coords(data)

def _load_netcdf_robust(base_path: Path, info: Dict, year: int, month: int, variables: List[str]) -> xr.Dataset:
    pattern = info.get('pattern', '*.nc')
    
    # Handle nested SWAMPS-like structure: YYYY/MM/*.nc
    if year and month:
        search_path = base_path / f"{year}" / f"{month:02d}" / pattern.replace('{year}', str(year)).replace('{month}', f'{month:02d}')
    elif year:
        search_path = base_path / f"{year}" / "**" / pattern.replace('{year}', str(year))
    else:
        search_path = base_path / "**" / pattern

    files = glob.glob(str(search_path), recursive=True)
    if not files:
        # Fallback to direct path if pattern parsing fails
        if 'file' in info:
            files = [str(base_path / info['file'])]
        else:
            raise FileNotFoundError(f"No files found for {info['name']} at {search_path}")

    logger.info(f"Loading {len(files)} files for {info['name']}")
    ds = xr.open_mfdataset(files, combine='by_coords', chunks={'lat': 1000, 'lon': 1000})
    
    if variables:
        ds = ds[variables]
    return ds

def _load_geotiff_robust(base_path: Path, info: Dict, year: int, month: int) -> xr.DataArray:
    # GWD30 annual pattern or static files
    if 'pattern' in info and year:
        file_path = str(base_path / info['pattern'].replace('{year}', str(year)))
    elif 'files' in info:
        file_key = 'wetland' if 'wetland' in info['files'] else list(info['files'].keys())[0]
        file_path = str(base_path / info['files'][file_key])
    else:
        # Just find any tif in the directory
        files = list(base_path.glob("*.tif"))
        if not files: raise FileNotFoundError(f"No TIFF files in {base_path}")
        file_path = str(files[0])

    da = rioxarray.open_rasterio(file_path, chunks=True)
    if da.ndim > 2:
        da = da.squeeze()
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