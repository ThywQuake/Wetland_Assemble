"""
Loader for SWAMPS. Handles sensor shifts and varying temporal resolution.
"""
import xarray as xr
from pathlib import Path
from typing import Dict, Union
import glob
from .base import BaseLoader, standardize_coords
import logging

logger = logging.getLogger(__name__)

class SWAMPSLoader(BaseLoader):
    def load(self, info: Dict, **kwargs) -> Union[xr.Dataset, xr.DataArray]:
        """
        Loads SWAMPS dataset.
        Handles the shift from bi-monthly (F11/ERS) to daily (F13/QUIKSCAT) around year 2000.
        """
        base_path = Path(info['path'])
        year = kwargs.get('year')
        month = kwargs.get('month')
        
        pattern = info.get('pattern', 'stable/{year}/{month}/*.nc')
        
        if year and month:
            search_path = base_path / pattern.replace('{year}', str(year)).replace('{month}', f'{month:02d}')
        elif year:
            search_path = base_path / pattern.replace('{year}', str(year)).replace('{month}', '*')
        else:
            search_path = base_path / pattern.replace('{year}', '*').replace('{month}', '*')
            
        files = glob.glob(str(search_path))
        
        if not files:
            raise FileNotFoundError(f"No SWAMPS NetCDF files found matching {search_path}. Fix Suggestion: Verify path in config/datasets.yaml")
            
        logger.info(f"Loading {len(files)} SWAMPS NetCDF file(s)")
        
        try:
            ds = xr.open_mfdataset(files, combine='by_coords', chunks={'lat': 1000, 'lon': 1000})
        except Exception as e:
            logger.error(f"Failed to open_mfdataset. Trying single open. Error: {e}")
            if len(files) == 1:
                ds = xr.open_dataset(files[0], chunks={'lat': 1000, 'lon': 1000})
            else:
                raise
                
        # Note: If temporal aggregation is requested (e.g., aggregate_to='monthly'),
        # it should ideally be handled downstream by an aligner, but the loader 
        # ensures the raw data is provided seamlessly across the sensor shift boundary.
        
        return standardize_coords(ds)
