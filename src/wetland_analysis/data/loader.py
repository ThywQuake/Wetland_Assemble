"""
Dataset loader factory for wetland datasets.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging

# Import specific loaders
from .loaders import (
    BaseLoader,
    GeoTIFFLoader,
    NetCDFLoader,
    GWD30Loader,
    GLWDLoader,
    TOPMODELLoader,
    SWAMPSLoader,
    BerkeleyLoader
)

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

class LoaderRegistry:
    """Registry mapping loader names to Loader instances."""
    def __init__(self):
        self._loaders: Dict[str, BaseLoader] = {
            'netcdf': NetCDFLoader(),
            'geotiff': GeoTIFFLoader(),
            'gwd30': GWD30Loader(),
            'glwd': GLWDLoader(),
            'topmodel': TOPMODELLoader(),
            'swamps': SWAMPSLoader(),
            'berkeley': BerkeleyLoader(),
        }

    def get_loader(self, loader_type: str) -> BaseLoader:
        loader = self._loaders.get(loader_type.lower())
        if not loader:
            raise ValueError(f"Unknown loader_type: {loader_type}. Available: {list(self._loaders.keys())}")
        return loader

# Global registry instance
_REGISTRY = LoaderRegistry()

def load_wetland_dataset(
    dataset_name: str,
    **kwargs
) -> Union['xr.Dataset', 'xr.DataArray']:
    """
    Robustly load a wetland dataset using tailored loaders based on config.
    
    Args:
        dataset_name: Name of the dataset defined in config/datasets.yaml
        **kwargs: Additional arguments passed to specific loaders (e.g., year, month, config, forcing, category)
    """
    logger.info(f"Loading dataset: {dataset_name} with args: {kwargs}")
    dataset_info = get_dataset_info(dataset_name.lower())
    
    # Determine loader type from config, fallback to basic format
    loader_type = dataset_info.get('loader_type', dataset_info.get('format', '').lower())
    
    loader = _REGISTRY.get_loader(loader_type)
    data = loader.load(dataset_info, **kwargs)
    
    if not validate_dataset_loaded(data, dataset_name):
        raise RuntimeError(f"Failed to validate loaded dataset: {dataset_name}")
        
    return data

def validate_dataset_loaded(
    data: Union['xr.Dataset', 'xr.DataArray'],
    dataset_name: str
) -> bool:
    """Validate that dataset was loaded correctly."""
    # Ensure xarray is available for type checking if needed
    import xarray as xr
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

    logger.info(f"Successfully validated dataset: {dataset_name}")
    return True