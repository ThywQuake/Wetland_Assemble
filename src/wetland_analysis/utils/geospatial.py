"""
Geospatial utility functions for coordinate alignment and resampling.
"""

import xarray as xr
import rioxarray
import numpy as np
from rasterio.enums import Resampling
from pathlib import Path
from typing import Union, Tuple, Any
import logging

logger = logging.getLogger(__name__)

def align_to_reference(
    ds: Union[xr.DataArray, xr.Dataset],
    reference: Union[xr.DataArray, xr.Dataset],
    is_categorical: bool = True
) -> Union[xr.DataArray, xr.Dataset]:
    """
    Align a dataset to a reference grid (e.g., 30m UTM) using reproject_match.
    
    Parameters
    ----------
    ds : xr.DataArray or xr.Dataset
        The dataset to be aligned.
    reference : xr.DataArray or xr.Dataset
        The reference grid dataset.
    is_categorical : bool, default True
        If True, uses 'mode' resampling (best for wetland/non-wetland classes).
        If False, uses 'bilinear' resampling (best for continuous probabilities).
        
    Returns
    -------
    xr.DataArray or xr.Dataset
        The aligned dataset matching the reference's CRS and transform.
    """
    resampling_method = Resampling.mode if is_categorical else Resampling.bilinear
    
    logger.info(f"Aligning dataset to reference using {resampling_method.name} resampling.")
    
    # Ensure CRS is present
    if ds.rio.crs is None:
        logger.warning("Input dataset missing CRS. Assuming EPSG:4326 if not specified.")
        ds.rio.write_crs("EPSG:4326", inplace=True)
        
    aligned_ds = ds.rio.reproject_match(
        reference,
        resampling=resampling_method
    )
    
    return aligned_ds

def create_30m_grid(
    bounds: Tuple[float, float, float, float],
    crs: str = "EPSG:4326"
) -> xr.DataArray:
    """
    Create an empty 30m reference grid for a given ROI.
    
    Parameters
    ----------
    bounds : Tuple[float, float, float, float]
        Bounding box (west, south, east, north).
    crs : str, default "EPSG:4326"
        Target coordinate system.
        
    Returns
    -------
    xr.DataArray
        An empty DataArray with the specified 30m resolution.
    """
    # Note: 30m in degrees is roughly 0.0002695
    # For precise 30m, we usually use UTM, but this provides a fallback.
    res = 0.0002695 
    
    west, south, east, north = bounds
    lons = np.arange(west, east, res)
    lats = np.arange(north, south, -res)
    
    grid = xr.DataArray(
        np.zeros((len(lats), len(lons)), dtype=np.float32),
        coords=[lats, lons],
        dims=["lat", "lon"],
        name="reference_grid"
    )
    grid.rio.write_crs(crs, inplace=True)
    return grid
