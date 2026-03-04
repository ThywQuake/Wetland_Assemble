"""
Dataset comparison functions for wetland analysis.
"""

import xarray as xr
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging

logger = logging.getLogger(__name__)


def compare_datasets(
    dataset1: xr.DataArray,
    dataset2: xr.DataArray,
    metrics: List[str] = None,
    threshold: float = 0.5,
    region: Optional[str] = None
) -> Dict:
    """
    Compare two wetland datasets using multiple metrics.

    Parameters
    ----------
    dataset1 : xr.DataArray
        First dataset
    dataset2 : xr.DataArray
        Second dataset
    metrics : list of str, optional
        Metrics to calculate. Options: 'accuracy', 'agreement', 'correlation', 'bias'
    threshold : float, optional
        Threshold for binary classification (if datasets are continuous)
    region : str, optional
        Region name for masking

    Returns
    -------
    dict
        Dictionary containing comparison results
    """
    if metrics is None:
        metrics = ['accuracy', 'agreement', 'correlation', 'bias']

    # Ensure datasets have same shape and coordinates
    if dataset1.shape != dataset2.shape:
        logger.warning("Dataset shapes differ, attempting to regrid...")
        # Simple regridding to common grid (for demonstration)
        # In production, use proper regridding function
        if 'lon' in dataset1.dims and 'lat' in dataset1.dims:
            # Interpolate dataset2 to dataset1 grid
            dataset2 = dataset2.interp(lon=dataset1.lon, lat=dataset1.lat, method='nearest')

    results = {}

    # Flatten arrays for comparison
    vals1 = dataset1.values.ravel()
    vals2 = dataset2.values.ravel()

    # Remove NaN values
    valid_mask = ~np.isnan(vals1) & ~np.isnan(vals2)
    vals1_valid = vals1[valid_mask]
    vals2_valid = vals2[valid_mask]

    n_valid = len(vals1_valid)
    if n_valid == 0:
        logger.error("No valid overlapping pixels for comparison")
        return {'error': 'no_valid_overlap'}

    for metric in metrics:
        if metric.lower() == 'accuracy':
            # Calculate accuracy metrics (for binary data)
            from .accuracy import calculate_spatial_accuracy
            try:
                # Convert to binary if needed
                if np.issubdtype(vals1_valid.dtype, np.floating):
                    ds1_bin = (vals1_valid > threshold).astype(int)
                    ds2_bin = (vals2_valid > threshold).astype(int)
                else:
                    ds1_bin = vals1_valid.astype(int)
                    ds2_bin = vals2_valid.astype(int)

                # Calculate accuracy
                acc_results = calculate_spatial_accuracy(
                    xr.DataArray(ds1_bin),
                    xr.DataArray(ds2_bin),
                    metrics=['OA', 'Kappa', 'PA', 'UA', 'F1', 'IoU']
                )
                results['accuracy'] = acc_results
            except Exception as e:
                logger.error(f"Error calculating accuracy: {e}")
                results['accuracy'] = {'error': str(e)}

        elif metric.lower() == 'agreement':
            # Calculate pixel agreement
            from .accuracy import calculate_pixel_agreement
            try:
                ds1_arr = xr.DataArray(vals1_valid.reshape(-1, 1))
                ds2_arr = xr.DataArray(vals2_valid.reshape(-1, 1))
                agreement = calculate_pixel_agreement(ds1_arr, ds2_arr, threshold)
                results['agreement'] = agreement
            except Exception as e:
                logger.error(f"Error calculating agreement: {e}")
                results['agreement'] = {'error': str(e)}

        elif metric.lower() == 'correlation':
            # Calculate correlation coefficients
            try:
                # Pearson correlation
                pearson_r = np.corrcoef(vals1_valid, vals2_valid)[0, 1]

                # Spearman correlation (rank-based)
                from scipy import stats
                spearman_rho, spearman_p = stats.spearmanr(vals1_valid, vals2_valid)

                # R-squared
                r_squared = pearson_r ** 2

                results['correlation'] = {
                    'pearson_r': float(pearson_r),
                    'spearman_rho': float(spearman_rho),
                    'spearman_p': float(spearman_p),
                    'r_squared': float(r_squared)
                }
            except Exception as e:
                logger.error(f"Error calculating correlation: {e}")
                results['correlation'] = {'error': str(e)}

        elif metric.lower() == 'bias':
            # Calculate bias and error metrics
            try:
                # Mean bias
                bias = np.mean(vals2_valid - vals1_valid)

                # Mean absolute error
                mae = np.mean(np.abs(vals2_valid - vals1_valid))

                # Root mean square error
                rmse = np.sqrt(np.mean((vals2_valid - vals1_valid) ** 2))

                # Normalized metrics (if data range is meaningful)
                data_range = np.ptp(vals1_valid)  # peak-to-peak
                if data_range > 0:
                    nmae = mae / data_range
                    nrmse = rmse / data_range
                else:
                    nmae = np.nan
                    nrmse = np.nan

                # Relative bias (percent)
                mean_val1 = np.mean(vals1_valid)
                if mean_val1 != 0:
                    rel_bias = bias / mean_val1 * 100
                else:
                    rel_bias = np.nan

                results['bias'] = {
                    'mean_bias': float(bias),
                    'mean_absolute_error': float(mae),
                    'root_mean_square_error': float(rmse),
                    'normalized_mae': float(nmae) if not np.isnan(nmae) else None,
                    'normalized_rmse': float(nrmse) if not np.isnan(nrmse) else None,
                    'relative_bias_percent': float(rel_bias) if not np.isnan(rel_bias) else None
                }
            except Exception as e:
                logger.error(f"Error calculating bias: {e}")
                results['bias'] = {'error': str(e)}

        else:
            logger.warning(f"Unknown comparison metric: {metric}")

    # Add summary statistics
    results['summary'] = {
        'n_valid_pixels': n_valid,
        'dataset1_stats': {
            'mean': float(np.mean(vals1_valid)),
            'std': float(np.std(vals1_valid)),
            'min': float(np.min(vals1_valid)),
            'max': float(np.max(vals1_valid))
        },
        'dataset2_stats': {
            'mean': float(np.mean(vals2_valid)),
            'std': float(np.std(vals2_valid)),
            'min': float(np.min(vals2_valid)),
            'max': float(np.max(vals2_valid))
        }
    }

    logger.info(f"Dataset comparison completed with {n_valid} valid pixels")
    return results


def calculate_agreement_metrics(
    datasets: Dict[str, xr.DataArray],
    reference_dataset: Optional[str] = None
) -> Dict[str, Dict]:
    """
    Calculate agreement metrics among multiple datasets.

    Parameters
    ----------
    datasets : dict
        Dictionary of dataset name -> xr.DataArray pairs
    reference_dataset : str, optional
        Name of reference dataset. If None, use pairwise comparisons.

    Returns
    -------
    dict
        Dictionary containing agreement metrics
    """
    dataset_names = list(datasets.keys())
    n_datasets = len(dataset_names)

    if n_datasets < 2:
        logger.error("Need at least 2 datasets for agreement analysis")
        return {}

    results = {}

    if reference_dataset:
        # Compare all datasets to reference
        if reference_dataset not in datasets:
            logger.error(f"Reference dataset '{reference_dataset}' not found")
            return {}

        ref_data = datasets[reference_dataset]

        for name, data in datasets.items():
            if name == reference_dataset:
                continue

            logger.info(f"Comparing {name} to reference {reference_dataset}")
            comparison = compare_datasets(ref_data, data, metrics=['accuracy', 'agreement', 'correlation', 'bias'])
            results[f"{reference_dataset}_vs_{name}"] = comparison

    else:
        # Pairwise comparisons
        for i in range(n_datasets - 1):
            for j in range(i + 1, n_datasets):
                name1 = dataset_names[i]
                name2 = dataset_names[j]

                logger.info(f"Comparing {name1} vs {name2}")
                comparison = compare_datasets(
                    datasets[name1], datasets[name2],
                    metrics=['accuracy', 'agreement', 'correlation', 'bias']
                )
                results[f"{name1}_vs_{name2}"] = comparison

    # Calculate ensemble agreement if more than 2 datasets
    if n_datasets > 2:
        logger.info("Calculating ensemble agreement...")
        ensemble_results = calculate_ensemble_agreement(datasets)
        results['ensemble'] = ensemble_results

    return results


def calculate_ensemble_agreement(
    datasets: Dict[str, xr.DataArray]
) -> Dict:
    """
    Calculate agreement among multiple datasets (ensemble analysis).

    Parameters
    ----------
    datasets : dict
        Dictionary of dataset name -> xr.DataArray pairs

    Returns
    -------
    dict
        Ensemble agreement metrics
    """
    dataset_list = list(datasets.values())
    n_datasets = len(dataset_list)

    # Stack datasets along a new dimension
    stacked = xr.concat(dataset_list, dim='dataset')

    # Calculate mean and std across datasets
    mean_data = stacked.mean(dim='dataset')
    std_data = stacked.std(dim='dataset')

    # Calculate consensus (pixels where most datasets agree)
    if n_datasets > 1:
        # For binary data: count agreements
        # For continuous data: calculate coefficient of variation
        cv_data = std_data / mean_data.where(mean_data != 0, other=np.nan)

        # Percent of pixels with low variability (CV < 0.5)
        low_var_pixels = np.sum(cv_data < 0.5) / cv_data.size * 100
    else:
        cv_data = None
        low_var_pixels = 0

    # Calculate pairwise correlations
    correlations = []
    for i in range(n_datasets - 1):
        for j in range(i + 1, n_datasets):
            vals_i = dataset_list[i].values.ravel()
            vals_j = dataset_list[j].values.ravel()

            valid_mask = ~np.isnan(vals_i) & ~np.isnan(vals_j)
            if np.sum(valid_mask) > 10:  # Need enough points
                corr = np.corrcoef(vals_i[valid_mask], vals_j[valid_mask])[0, 1]
                if not np.isnan(corr):
                    correlations.append(corr)

    avg_correlation = np.mean(correlations) if correlations else np.nan

    results = {
        'n_datasets': n_datasets,
        'mean_data_shape': mean_data.shape,
        'variability': {
            'mean_std': float(std_data.mean().values),
            'max_std': float(std_data.max().values),
            'cv_mean': float(cv_data.mean().values) if cv_data is not None else None,
            'low_variability_pixels_percent': float(low_var_pixels)
        },
        'correlation': {
            'average_pairwise': float(avg_correlation),
            'min_pairwise': float(np.min(correlations)) if correlations else None,
            'max_pairwise': float(np.max(correlations)) if correlations else None
        }
    }

    logger.info(f"Ensemble analysis: {n_datasets} datasets, avg correlation: {avg_correlation:.3f}")
    return results


def analyze_spatial_patterns(
    dataset: xr.DataArray,
    mask: Optional[xr.DataArray] = None,
    spatial_scale: float = 1.0
) -> Dict:
    """
    Analyze spatial patterns in a dataset.

    Parameters
    ----------
    dataset : xr.DataArray
        Input dataset
    mask : xr.DataArray, optional
        Mask to apply (True = include, False/NaN = exclude)
    spatial_scale : float, optional
        Spatial scale for pattern analysis (degrees)

    Returns
    -------
    dict
        Spatial pattern metrics
    """
    # Apply mask if provided
    if mask is not None:
        data_masked = dataset.where(mask, other=np.nan)
    else:
        data_masked = dataset

    # Remove NaN values
    valid_data = data_masked.values[~np.isnan(data_masked.values)]

    if len(valid_data) == 0:
        logger.error("No valid data for spatial pattern analysis")
        return {'error': 'no_valid_data'}

    # Basic spatial statistics
    results = {
        'basic_statistics': {
            'n_valid_pixels': len(valid_data),
            'mean': float(np.mean(valid_data)),
            'std': float(np.std(valid_data)),
            'min': float(np.min(valid_data)),
            'max': float(np.max(valid_data)),
            'median': float(np.median(valid_data)),
            'skewness': float(stats.skew(valid_data)),
            'kurtosis': float(stats.kurtosis(valid_data))
        }
    }

    # Spatial autocorrelation (Moran's I approximation)
    try:
        # Simple spatial correlation (for demonstration)
        # In production, use proper spatial autocorrelation function
        if 'lon' in dataset.dims and 'lat' in dataset.dims:
            # Calculate gradient magnitude as spatial variability measure
            grad_lon = np.gradient(data_masked.values, axis=data_masked.dims.index('lon'))
            grad_lat = np.gradient(data_masked.values, axis=data_masked.dims.index('lat'))
            grad_magnitude = np.sqrt(grad_lon**2 + grad_lat**2)

            results['spatial_variability'] = {
                'gradient_mean': float(np.nanmean(grad_magnitude)),
                'gradient_std': float(np.nanstd(grad_magnitude)),
                'spatial_heterogeneity': float(np.nanstd(grad_magnitude) / np.nanmean(grad_magnitude))
            }
    except Exception as e:
        logger.error(f"Error calculating spatial variability: {e}")

    logger.info(f"Spatial pattern analysis completed: {len(valid_data)} valid pixels")
    return results