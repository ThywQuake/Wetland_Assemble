"""
Loader for TOPMODEL. Handles hierarchical directory structures.
"""
import xarray as xr
from pathlib import Path
from typing import Dict, Union
import glob
from .base import BaseLoader, standardize_coords
import logging

logger = logging.getLogger(__name__)

class TOPMODELLoader(BaseLoader):
    def load(self, info: Dict, **kwargs) -> Union[xr.Dataset, xr.DataArray]:
        """
        Loads TOPMODEL dataset.
        Args:
            config (str): The configuration layer (e.g., 'G2017_max'). Required.
            forcing (str): The forcing layer (e.g., 'ERA5'). Required.
            year (int): Optional year to load.
        """
        base_path = Path(info['path'])
        
        config = kwargs.get('config')
        forcing = kwargs.get('forcing')
        year = kwargs.get('year')
        
        if not config or not forcing:
            raise ValueError("TOPMODELLoader requires 'config' and 'forcing' arguments. Example: config='G2017_max', forcing='ERA5'")
            
        # Build path based on pattern: {config}/{forcing}/fwet_{config}_{forcing}_reso025_{year}.nc
        pattern = info.get('pattern', '{config}/{forcing}/fwet_{config}_{forcing}_reso025_{year}.nc')
        
        # Replace known parts
        path_str = pattern.replace('{config}', config).replace('{forcing}', forcing)
        
        if year:
            search_path = base_path / path_str.replace('{year}', str(year))
        else:
            # Load all years for this config/forcing combination
            search_path = base_path / path_str.replace('{year}', '*')
            
        files = glob.glob(str(search_path))
        if not files:
            raise FileNotFoundError(f"No TOPMODEL files found matching {search_path}. Fix Suggestion: Verify config/forcing values and datasets.yaml path.")
            
        logger.info(f"Loading {len(files)} TOPMODEL NetCDF file(s) for {config}/{forcing}")
        
        try:
            ds = xr.open_mfdataset(files, combine='by_coords', chunks={'lat': 1000, 'lon': 1000})
        except Exception as e:
            logger.error(f"Failed to open_mfdataset. Trying single open. Error: {e}")
            if len(files) == 1:
                ds = xr.open_dataset(files[0], chunks={'lat': 1000, 'lon': 1000})
            else:
                raise
                
        return standardize_coords(ds)
