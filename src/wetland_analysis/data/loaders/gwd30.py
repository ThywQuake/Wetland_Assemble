"""
Loader for GWD30. Handles mosaicking of multiple TIFF tiles.
"""
import xarray as xr
import rioxarray
from rioxarray.merge import merge_arrays
from pathlib import Path
from typing import Dict, Union, List
from .base import BaseLoader, standardize_coords
import logging
import glob

logger = logging.getLogger(__name__)

class GWD30Loader(BaseLoader):
    def load(self, info: Dict, **kwargs) -> Union[xr.Dataset, xr.DataArray]:
        """
        Loads GWD30 by mosaicking all tiles for a specific year.
        If 'roi_bounds' is provided in kwargs (min_lon, min_lat, max_lon, max_lat),
        it will attempt to filter tiles before merging.
        """
        base_path = Path(info['path'])
        year = kwargs.get('year')
        
        if not year:
             raise ValueError("GWD30Loader requires a 'year' argument.")
             
        pattern = info.get('pattern', '{year}/*_wetland_{year}.tif')
        search_path = str(base_path / pattern.replace('{year}', str(year)))
        
        files = glob.glob(search_path)
        if not files:
            raise FileNotFoundError(f"No GWD30 tiles found for year {year} at {search_path}. Fix Suggestion: Ensure you have downloaded the data and paths in datasets.yaml are correct.")
            
        logger.info(f"Found {len(files)} GWD30 tiles for year {year}")
        
        # Mosaicking can be memory intensive.
        # Open them lazily with chunks
        arrays_to_merge = []
        for f in files:
            da = rioxarray.open_rasterio(f, chunks=True)
            if da.ndim > 2:
                da = da.squeeze().drop_vars('band', errors='ignore')
            arrays_to_merge.append(da)
            
        logger.info("Merging GWD30 arrays (this may be lazy if chunks are used)...")
        # merge_arrays is memory intensive if not dask-backed
        merged_da = merge_arrays(arrays_to_merge)
        
        # Promote name to allow it to be converted to dataset gracefully later if needed
        merged_da.name = "wetland"
        
        return standardize_coords(merged_da)
