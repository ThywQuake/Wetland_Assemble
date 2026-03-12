"""
Generic NetCDF loader.
"""
import xarray as xr
from pathlib import Path
from typing import Dict, Union
import glob
from .base import BaseLoader, standardize_coords
import logging

logger = logging.getLogger(__name__)

class NetCDFLoader(BaseLoader):
    def load(self, info: Dict, **kwargs) -> Union[xr.Dataset, xr.DataArray]:
        base_path = Path(info['path'])
        pattern = info.get('pattern', '*.nc')
        
        # We handle year/month in generic if they exist, but derived loaders can do more complex logic
        year = kwargs.get('year')
        month = kwargs.get('month')
        variables = kwargs.get('variables', info.get('variables'))
        
        if year and month:
            search_path = base_path / f"{year}" / f"{month:02d}" / pattern.replace('{year}', str(year)).replace('{month}', f'{month:02d}')
        elif year:
            search_path = base_path / f"{year}" / "**" / pattern.replace('{year}', str(year))
        else:
            search_path = base_path / "**" / pattern

        files = glob.glob(str(search_path), recursive=True)
        if not files:
            if 'file' in info:
                files = [str(base_path / info['file'])]
            else:
                raise FileNotFoundError(f"No files found matching {search_path}. Fix Suggestion: Verify path and pattern in config/datasets.yaml")

        logger.info(f"Loading {len(files)} NetCDF file(s)")
        
        try:
            ds = xr.open_mfdataset(files, combine='by_coords', chunks={'lat': 1000, 'lon': 1000})
        except Exception as e:
            logger.error(f"Failed to open_mfdataset. Trying single open. Error: {e}")
            if len(files) == 1:
                ds = xr.open_dataset(files[0], chunks={'lat': 1000, 'lon': 1000})
            else:
                raise
        
        if variables:
            # If variables is a dictionary (like in our config: {watermask: "water_mask"})
            if isinstance(variables, dict):
                # Only keep variables present in the dataset to avoid KeyError
                keep_vars = [v for k, v in variables.items() if v in ds]
                if keep_vars:
                    ds = ds[keep_vars]
            elif isinstance(variables, list):
                 keep_vars = [v for v in variables if v in ds]
                 if keep_vars:
                     ds = ds[keep_vars]

        return standardize_coords(ds)
