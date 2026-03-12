"""
Loader for Berkeley datasets.
"""
import xarray as xr
from pathlib import Path
from typing import Dict, Union
import glob
from .base import BaseLoader, standardize_coords
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class BerkeleyLoader(BaseLoader):
    def load(self, info: Dict, **kwargs) -> Union[xr.Dataset, xr.DataArray]:
        """
        Loads Berkeley dataset and reconstructs the time dimension from filenames if missing.
        """
        base_path = Path(info['path'])
        pattern = info.get('pattern', 'cyg.ddmi.*.l3.uc-berkeley-watermask-monthly.a31.d32.nc')
        
        year = kwargs.get('year')
        month = kwargs.get('month')
        
        if year and month:
            # Pattern specific to Berkeley: YYYY-MM
            date_str = f"{year}-{month:02d}"
            search_path = base_path / pattern.replace('*', date_str)
        elif year:
            search_path = base_path / pattern.replace('*', f"{year}-*")
        else:
            search_path = base_path / pattern

        files = glob.glob(str(search_path))
        if not files:
            raise FileNotFoundError(f"No Berkeley files found matching {search_path}. Fix Suggestion: Verify path in config/datasets.yaml")
            
        logger.info(f"Loading {len(files)} Berkeley file(s)")
        
        try:
            ds = xr.open_mfdataset(files, combine='by_coords', chunks={'lat': 1000, 'lon': 1000})
        except Exception as e:
            logger.error(f"Failed to open_mfdataset. Trying single open. Error: {e}")
            if len(files) == 1:
                ds = xr.open_dataset(files[0], chunks={'lat': 1000, 'lon': 1000})
            else:
                raise
                
        # Berkeley sometimes has time encoded in file name but not as a proper dimension.
        # Ensure time dimension exists. (If it already exists, open_mfdataset usually handles it,
        # but this is a safeguard).
        if 'time' not in ds.dims and len(files) == 1:
             # Try to extract time from filename, e.g., cyg.ddmi.2018-08.l3...
             filename = Path(files[0]).name
             parts = filename.split('.')
             if len(parts) > 2:
                 date_part = parts[2] # 2018-08
                 try:
                     time_val = pd.to_datetime(date_part)
                     ds = ds.assign_coords(time=[time_val])
                 except Exception as err:
                     logger.warning(f"Could not parse time from filename {filename}: {err}")
                     
        return standardize_coords(ds)
