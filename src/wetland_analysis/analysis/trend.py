"""
Trend analysis functions for wetland time series.
"""

import xarray as xr
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from scipy import stats

logger = logging.getLogger(__name__)


def calculate_mann_kendall_trend(
    time_series: Union[xr.DataArray, np.ndarray],
    alpha: float = 0.05
) -> Dict[str, Union[float, bool, str]]:
    """
    Calculate Mann-Kendall trend test for a time series.

    Parameters
    ----------
    time_series : xr.DataArray or np.ndarray
        Time series data (1D)
    alpha : float, optional
        Significance level

    Returns
    -------
    dict
        Dictionary containing Mann-Kendall test results
    """
    # Convert to numpy array
    if isinstance(time_series, xr.DataArray):
        y = time_series.values
    else:
        y = np.asarray(time_series)

    # Remove NaN values
    valid_mask = ~np.isnan(y)
    y_clean = y[valid_mask]
    n = len(y_clean)

    if n < 4:
        logger.warning(f"Not enough data points for Mann-Kendall test: n={n}")
        return {
            'trend': 'insufficient_data',
            'slope': np.nan,
            'p_value': 1.0,
            'significant': False,
            'z_score': 0.0,
            'n': n
        }

    # Calculate Mann-Kendall test
    # Create all possible pairs
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            s += np.sign(y_clean[j] - y_clean[i])

    # Calculate variance
    var_s = (n * (n - 1) * (2 * n + 5)) / 18

    # Calculate Z-score
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0

    # Calculate p-value (two-tailed test)
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    # Determine trend direction
    if p_value < alpha:
        if z > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        significant = True
    else:
        trend = 'no_trend'
        significant = False

    results = {
        'trend': trend,
        'slope': np.nan,  # Will be calculated separately with Sen's slope
        'p_value': float(p_value),
        'significant': significant,
        'z_score': float(z),
        's_statistic': int(s),
        'variance_s': float(var_s),
        'n': n
    }

    logger.info(f"Mann-Kendall test: {trend}, p={p_value:.4f}, significant={significant}")
    return results


def calculate_sens_slope(
    time_series: Union[xr.DataArray, np.ndarray],
    time_values: Optional[Union[np.ndarray, List]] = None
) -> Dict[str, Union[float, List]]:
    """
    Calculate Sen's slope for a time series.

    Parameters
    ----------
    time_series : xr.DataArray or np.ndarray
        Time series data (1D)
    time_values : np.ndarray or list, optional
        Time values. If None, use indices.

    Returns
    -------
    dict
        Dictionary containing Sen's slope results
    """
    # Convert to numpy array
    if isinstance(time_series, xr.DataArray):
        y = time_series.values
    else:
        y = np.asarray(time_series)

    # Remove NaN values
    valid_mask = ~np.isnan(y)
    y_clean = y[valid_mask]

    if time_values is None:
        x = np.arange(len(y))[valid_mask]
    else:
        x = np.asarray(time_values)[valid_mask]

    n = len(x)

    if n < 2:
        logger.warning(f"Not enough data points for Sen's slope: n={n}")
        return {
            'slope': np.nan,
            'intercept': np.nan,
            'slopes': [],
            'n': n
        }

    # Calculate slopes between all pairs
    slopes = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            slope = (y_clean[j] - y_clean[i]) / (x[j] - x[i])
            if not np.isnan(slope) and not np.isinf(slope):
                slopes.append(slope)

    if len(slopes) == 0:
        logger.warning("No valid slopes calculated")
        return {
            'slope': np.nan,
            'intercept': np.nan,
            'slopes': [],
            'n': n
        }

    # Calculate median slope
    slope = np.median(slopes)

    # Calculate intercept using median of y - slope * x
    intercept = np.median(y_clean - slope * x)

    results = {
        'slope': float(slope),
        'intercept': float(intercept),
        'slopes': slopes,
        'n_slopes': len(slopes),
        'n': n
    }

    logger.info(f"Sen's slope: {slope:.6f}, intercept: {intercept:.6f}")
    return results


def analyze_temporal_trends(
    data: xr.DataArray,
    time_dim: str = 'time',
    alpha: float = 0.05
) -> xr.Dataset:
    """
    Analyze temporal trends for each pixel in a time series dataset.

    Parameters
    ----------
    data : xr.DataArray
        Spatiotemporal data with time dimension
    time_dim : str, optional
        Name of time dimension
    alpha : float, optional
        Significance level for Mann-Kendall test

    Returns
    -------
    xr.Dataset
        Dataset containing trend analysis results for each pixel
    """
    if time_dim not in data.dims:
        raise ValueError(f"Time dimension '{time_dim}' not found in data")

    # Get shape information
    spatial_dims = [dim for dim in data.dims if dim != time_dim]
    spatial_shape = [data.sizes[dim] for dim in spatial_dims]

    # Initialize result arrays
    trend_map = np.full(spatial_shape, np.nan, dtype='U20')
    slope_map = np.full(spatial_shape, np.nan)
    p_value_map = np.full(spatial_shape, np.nan)
    significance_map = np.full(spatial_shape, False)

    # Reshape data for pixel-wise processing
    data_flat = data.stack(pixel=spatial_dims).transpose('pixel', time_dim)
    n_pixels = data_flat.shape[0]

    logger.info(f"Analyzing trends for {n_pixels} pixels...")

    # Process each pixel
    for i in range(n_pixels):
        pixel_series = data_flat[i, :]

        # Skip if all NaN
        if np.all(np.isnan(pixel_series)):
            continue

        # Calculate Mann-Kendall trend
        mk_result = calculate_mann_kendall_trend(pixel_series, alpha)

        # Calculate Sen's slope
        sen_result = calculate_sens_slope(pixel_series)

        # Get spatial indices
        idx = np.unravel_index(i, spatial_shape)

        # Store results
        trend_map[idx] = mk_result['trend']
        slope_map[idx] = sen_result['slope']
        p_value_map[idx] = mk_result['p_value']
        significance_map[idx] = mk_result['significant']

        # Log progress
        if (i + 1) % 10000 == 0 or (i + 1) == n_pixels:
            logger.info(f"Processed {i + 1}/{n_pixels} pixels")

    # Create result dataset
    coords = {dim: data[dim] for dim in spatial_dims}

    result_ds = xr.Dataset({
        'trend': (spatial_dims, trend_map),
        'slope': (spatial_dims, slope_map),
        'p_value': (spatial_dims, p_value_map),
        'significant': (spatial_dims, significance_map)
    }, coords=coords)

    # Add attributes
    result_ds.attrs['analysis'] = 'temporal_trend_analysis'
    result_ds.attrs['method'] = 'Mann_Kendall_Sens_Slope'
    result_ds.attrs['alpha'] = alpha
    result_ds.attrs['time_dimension'] = time_dim

    logger.info("Trend analysis completed")
    return result_ds


def calculate_trend_metrics(
    trend_results: xr.Dataset
) -> Dict[str, Union[float, int, Dict]]:
    """
    Calculate summary metrics from trend analysis results.

    Parameters
    ----------
    trend_results : xr.Dataset
        Dataset containing trend analysis results

    Returns
    -------
    dict
        Summary metrics
    """
    # Extract data arrays
    trend = trend_results['trend']
    slope = trend_results['slope']
    significant = trend_results['significant']

    # Count pixels by trend type
    valid_mask = ~np.isnan(slope.values)
    trend_values = trend.values[valid_mask]
    significant_values = significant.values[valid_mask]

    # Count trends
    increasing = np.sum((trend_values == 'increasing') & significant_values)
    decreasing = np.sum((trend_values == 'decreasing') & significant_values)
    no_trend_sig = np.sum((trend_values == 'no_trend') & significant_values)
    no_trend_insig = np.sum(~significant_values)

    total_pixels = len(trend_values)

    # Slope statistics
    slope_values = slope.values[valid_mask]
    slope_mean = np.nanmean(slope_values)
    slope_std = np.nanstd(slope_values)
    slope_min = np.nanmin(slope_values)
    slope_max = np.nanmax(slope_values)

    # Percentage of significant trends
    percent_significant = (np.sum(significant_values) / total_pixels * 100) if total_pixels > 0 else 0

    metrics = {
        'total_pixels': int(total_pixels),
        'increasing_trend_pixels': int(increasing),
        'decreasing_trend_pixels': int(decreasing),
        'no_trend_pixels': int(no_trend_sig + no_trend_insig),
        'significant_pixels': int(np.sum(significant_values)),
        'percent_significant': float(percent_significant),
        'slope_statistics': {
            'mean': float(slope_mean),
            'std': float(slope_std),
            'min': float(slope_min),
            'max': float(slope_max)
        },
        'trend_distribution': {
            'increasing_percent': float(increasing / total_pixels * 100) if total_pixels > 0 else 0,
            'decreasing_percent': float(decreasing / total_pixels * 100) if total_pixels > 0 else 0,
            'no_trend_percent': float((no_trend_sig + no_trend_insig) / total_pixels * 100) if total_pixels > 0 else 0
        }
    }

    logger.info(f"Trend metrics: {percent_significant:.1f}% significant trends "
                f"(↑{increasing/total_pixels*100:.1f}%, ↓{decreasing/total_pixels*100:.1f}%)")

    return metrics