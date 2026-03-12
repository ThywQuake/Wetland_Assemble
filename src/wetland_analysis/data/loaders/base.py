"""
Base loader class for the Loader Factory pattern.
"""
from abc import ABC, abstractmethod
from typing import Union, Optional, List, Dict
import xarray as xr
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

def standardize_coords(ds: Union[xr.Dataset, xr.DataArray]) -> Union[xr.Dataset, xr.DataArray]:
    """Ensure dimensions are consistently named 'lat' and 'lon'."""
    rename_dict = {old: new for old, new in COORD_MAP.items() if old in ds.dims}
    if rename_dict:
        logger.debug(f"Standardizing coordinates: {rename_dict}")
        ds = ds.rename(rename_dict)
    return ds

class BaseLoader(ABC):
    """Abstract base class for all dataset loaders."""
    
    @abstractmethod
    def load(self, info: Dict, **kwargs) -> Union[xr.Dataset, xr.DataArray]:
        """
        Load dataset based on config info and runtime arguments.
        
        Args:
            info (Dict): Dataset configuration from datasets.yaml
            **kwargs: Additional runtime arguments (e.g., year, month, roi, forcing)
            
        Returns:
            Union[xr.Dataset, xr.DataArray]: The loaded data.
        """
        pass
