"""
Data preprocessing functions for wetland datasets.
"""

import xarray as xr
import numpy as np
from typing import Tuple, Optional, Union
import logging

logger = logging.getLogger(__name__)


def resample_to_common_grid(
    data: Union[xr.Dataset, xr.DataArray],
    target_resolution: float,
    method: str = 'nearest'
) -> Union[xr.Dataset, xr.DataArray]:
    """
    Resample data to a common grid resolution.

    Parameters
    ----------
    data : xr.Dataset or xr.DataArray
        Input data
    target_resolution : float
        Target resolution in degrees
    method : str, optional
        Resampling method: 'nearest', 'linear', 'cubic'

    Returns
    -------
    xr.Dataset or xr.DataArray
        Resampled data
    """
    # Get current resolution from coordinates
    if 'lon' in data.dims and 'lat' in data.dims:
        lon_diff = np.diff(data.lon.values).mean()
        lat_diff = np.diff(data.lat.values).mean()
        current_res = max(abs(lon_diff), abs(lat_diff))
    elif 'x' in data.dims and 'y' in data.dims:
        x_diff = np.diff(data.x.values).mean()
        y_diff = np.diff(data.y.values).mean()
        current_res = max(abs(x_diff), abs(y_diff))
    else:
        raise ValueError("Cannot determine current resolution from data dimensions")

    # Check if resampling is needed
    if abs(current_res - target_resolution) < 1e-10:
        logger.info(f"Data already at target resolution: {target_resolution}°")
        return data

    # Calculate resampling factor
    factor = current_res / target_resolution

    if factor > 1:  # Upsampling
        logger.info(f"Upsampling from {current_res}° to {target_resolution}° (factor: {factor:.2f})")
        if method == 'nearest':
            resampled = data.interp(
                lon=np.arange(data.lon.min(), data.lon.max() + target_resolution, target_resolution),
                lat=np.arange(data.lat.min(), data.lat.max() + target_resolution, target_resolution),
                method='nearest'
            )
        else:
            resampled = data.interpolate_na(dim='lon', method=method).interpolate_na(dim='lat', method=method)
    else:  # Downsampling
        logger.info(f"Downsampling from {current_res}° to {target_resolution}° (factor: {factor:.2f})")
        resampled = data.coarsen(lon=int(1/factor), lat=int(1/factor), boundary='trim').mean()

    return resampled


def mask_region(
    data: Union[xr.Dataset, xr.DataArray],
    bbox: Tuple[float, float, float, float],
    mask_outside: bool = True
) -> Union[xr.Dataset, xr.DataArray]:
    """
    Mask data to a specific region defined by bounding box.

    Parameters
    ----------
    data : xr.Dataset or xr.DataArray
        Input data
    bbox : tuple
        Bounding box (min_lon, min_lat, max_lon, max_lat)
    mask_outside : bool, optional
        If True, mask values outside bbox (set to NaN).
        If False, mask values inside bbox.

    Returns
    -------
    xr.Dataset or xr.DataArray
        Masked data
    """
    min_lon, min_lat, max_lon, max_lat = bbox

    # Create mask based on coordinates
    if 'lon' in data.coords and 'lat' in data.coords:
        lon_mask = (data.lon >= min_lon) & (data.lon <= max_lon)
        lat_mask = (data.lat >= min_lat) & (data.lat <= max_lat)
        region_mask = lon_mask & lat_mask
    elif 'x' in data.coords and 'y' in data.coords:
        # Assuming x is longitude and y is latitude
        x_mask = (data.x >= min_lon) & (data.x <= max_lon)
        y_mask = (data.y >= min_lat) & (data.y <= max_lat)
        region_mask = x_mask & y_mask
    else:
        raise ValueError("Data must have lon/lat or x/y coordinates")

    # Apply mask
    if mask_outside:
        # Keep only data inside bbox, mask outside
        masked = data.where(region_mask, other=np.nan)
    else:
        # Keep only data outside bbox, mask inside
        masked = data.where(~region_mask, other=np.nan)

    logger.info(f"Masked region: {bbox} (mask_outside={mask_outside})")
    return masked


def normalize_data(
    data: Union[xr.Dataset, xr.DataArray],
    method: str = 'minmax',
    feature_range: Tuple[float, float] = (0, 1)
) -> Union[xr.Dataset, xr.DataArray]:
    """
    Normalize data values.

    Parameters
    ----------
    data : xr.Dataset or xr.DataArray
        Input data
    method : str, optional
        Normalization method: 'minmax', 'zscore', 'log'
    feature_range : tuple, optional
        Output range for minmax normalization

    Returns
    -------
    xr.Dataset or xr.DataArray
        Normalized data
    """
    if method == 'minmax':
        min_val = data.min().values
        max_val = data.max().values
        if np.isclose(min_val, max_val):
            logger.warning("Min and max values are equal, normalization may produce NaN")
            return data * 0 + feature_range[0]

        a, b = feature_range
        normalized = a + (data - min_val) * (b - a) / (max_val - min_val)
        logger.info(f"Min-max normalized to range {feature_range}")

    elif method == 'zscore':
        mean_val = data.mean().values
        std_val = data.std().values
        if std_val == 0:
            logger.warning("Standard deviation is zero, z-score normalization would produce NaN")
            return data * 0

        normalized = (data - mean_val) / std_val
        logger.info("Z-score normalized (mean=0, std=1)")

    elif method == 'log':
        if (data <= 0).any():
            logger.warning("Data contains non-positive values, adding small offset for log")
            data = data.where(data > 0, other=1e-10)
        normalized = np.log1p(data)  # log(1 + x) for stability
        logger.info("Log transformed")

    else:
        raise ValueError(f"Unknown normalization method: {method}")

    return normalized


def fill_missing_values(
    data: Union[xr.Dataset, xr.DataArray],
    method: str = 'linear',
    limit: Optional[int] = None
) -> Union[xr.Dataset, xr.DataArray]:
    """
    Fill missing (NaN) values in data.

    Parameters
    ----------
    data : xr.Dataset or xr.DataArray
        Input data with missing values
    method : str, optional
        Interpolation method: 'linear', 'nearest', 'cubic', 'ffill', 'bfill'
    limit : int, optional
        Maximum number of consecutive NaN values to fill

    Returns
    --
    xr.Dataset or xr.DataArray
        Data with filled missing values
    """
    # Count missing values before filling
    missing_count = np.isnan(data.values).sum()
    if missing_count == 0:
        logger.info("No missing values to fill")
        return data

    logger.info(f"Filling {missing_count} missing values using {method} method")

    if method in ['linear', 'nearest', 'cubic']:
        # Spatial/temporal interpolation
        if 'time' in data.dims:
            # Temporal interpolation
            filled = data.interpolate_na(dim='time', method=method, limit=limit)
        elif 'lon' in data.dims and 'lat' in data.dims:
            # Spatial interpolation
            filled = data.interpolate_na(dim='lon', method=method, limit=limit)
            filled = filled.interpolate_na(dim='lat', method=method, limit=limit)
        else:
            # Generic interpolation
            filled = data.interpolate_na(method=method, limit=limit)

    elif method == 'ffill':
        # Forward fill
        filled = data.ffill(dim='time' if 'time' in data.dims else None, limit=limit)

    elif method == 'bfill':
        # Backward fill
        filled = data.bfill(dim='time' if 'time' in data.dims else None, limit=limit)

    else:
        raise ValueError(f"Unknown fill method: {method}")

    # Count remaining missing values
    remaining_missing = np.isnan(filled.values).sum()
    logger.info(f"Missing values filled: {missing_count - remaining_missing}, "
                f"remaining: {remaining_missing}")

    return filled