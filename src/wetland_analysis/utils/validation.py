"""
Validation utilities for wetland analysis.
"""

import xarray as xr
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any
import logging

logger = logging.getLogger(__name__)


def validate_inputs(
    data: Union[xr.DataArray, xr.Dataset, np.ndarray],
    required_dims: Optional[List[str]] = None,
    required_shape: Optional[Tuple[int, ...]] = None,
    required_dtype: Optional[Union[str, type]] = None,
    check_nan: bool = True,
    check_finite: bool = True
) -> Dict[str, Any]:
    """
    Validate input data.

    Parameters
    ----------
    data : xr.DataArray, xr.Dataset, or np.ndarray
        Input data to validate
    required_dims : list of str, optional
        Required dimension names (for xarray objects)
    required_shape : tuple, optional
        Required shape
    required_dtype : str or type, optional
        Required data type
    check_nan : bool, optional
        Check for NaN values
    check_finite : bool, optional
        Check for finite values (not NaN or inf)

    Returns
    -------
    dict
        Validation results
    """
    validation_results = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }

    # Check data type
    if required_dtype is not None:
        if isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset):
            actual_dtype = str(data.dtype)
        else:
            actual_dtype = str(data.dtype)

        required_dtype_str = str(required_dtype)
        if actual_dtype != required_dtype_str:
            validation_results['errors'].append(
                f"Data type mismatch: expected {required_dtype_str}, got {actual_dtype}"
            )

    # Check shape
    if required_shape is not None:
        actual_shape = data.shape if hasattr(data, 'shape') else None
        if actual_shape != required_shape:
            validation_results['errors'].append(
                f"Shape mismatch: expected {required_shape}, got {actual_shape}"
            )

    # Check dimensions (for xarray objects)
    if required_dims is not None and (isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset)):
        actual_dims = list(data.dims)
        missing_dims = [dim for dim in required_dims if dim not in actual_dims]
        if missing_dims:
            validation_results['errors'].append(
                f"Missing dimensions: {missing_dims}"
            )

    # Check for NaN values
    if check_nan:
        if isinstance(data, (xr.DataArray, xr.Dataset)):
            nan_count = np.isnan(data.values).sum()
        else:
            nan_count = np.isnan(data).sum()

        if nan_count > 0:
            validation_results['warnings'].append(
                f"Found {nan_count} NaN values in data"
            )

    # Check for finite values
    if check_finite:
        if isinstance(data, (xr.DataArray, xr.Dataset)):
            finite_mask = np.isfinite(data.values)
        else:
            finite_mask = np.isfinite(data)

        non_finite_count = (~finite_mask).sum()

        if non_finite_count > 0:
            validation_results['warnings'].append(
                f"Found {non_finite_count} non-finite values in data"
            )

    # Update validity
    if validation_results['errors']:
        validation_results['is_valid'] = False
        logger.error(f"Input validation failed: {validation_results['errors']}")
    elif validation_results['warnings']:
        logger.warning(f"Input validation warnings: {validation_results['warnings']}")
    else:
        logger.info("Input validation passed")

    return validation_results


def check_data_consistency(
    datasets: Dict[str, Union[xr.DataArray, xr.Dataset]],
    check_coords: bool = True,
    check_shape: bool = True,
    check_dtype: bool = False
) -> Dict[str, Any]:
    """
    Check consistency among multiple datasets.

    Parameters
    ----------
    datasets : dict
        Dictionary of dataset name -> data pairs
    check_coords : bool, optional
        Check coordinate consistency
    check_shape : bool, optional
        Check shape consistency
    check_dtype : bool, optional
        Check data type consistency

    Returns
    -------
    dict
        Consistency check results
    """
    if len(datasets) < 2:
        return {'is_consistent': True, 'issues': []}

    consistency_results = {
        'is_consistent': True,
        'issues': [],
        'comparisons': {}
    }

    dataset_names = list(datasets.keys())
    reference_name = dataset_names[0]
    reference_data = datasets[reference_name]

    # Get reference properties
    if isinstance(reference_data, (xr.DataArray, xr.Dataset)):
        ref_shape = reference_data.shape
        ref_dtype = str(reference_data.dtype)
        if check_coords:
            ref_coords = {dim: reference_data[dim].values for dim in reference_data.dims}
    else:
        ref_shape = reference_data.shape
        ref_dtype = str(reference_data.dtype)
        ref_coords = None

    # Compare each dataset to reference
    for name, data in datasets.items():
        if name == reference_name:
            continue

        comparisons = []

        # Check shape
        if check_shape and hasattr(data, 'shape'):
            if data.shape != ref_shape:
                comparisons.append(f"Shape mismatch: {data.shape} vs {ref_shape}")
                consistency_results['is_consistent'] = False

        # Check dtype
        if check_dtype and hasattr(data, 'dtype'):
            data_dtype = str(data.dtype)
            if data_dtype != ref_dtype:
                comparisons.append(f"Dtype mismatch: {data_dtype} vs {ref_dtype}")
                # This is usually a warning, not an error
                consistency_results['issues'].append(f"Dtype mismatch for {name}")

        # Check coordinates (for xarray objects)
        if check_coords and isinstance(data, (xr.DataArray, xr.Dataset)) and ref_coords:
            data_coords = {dim: data[dim].values for dim in data.dims}

            # Check coordinate dimensions match
            if set(data_coords.keys()) != set(ref_coords.keys()):
                comparisons.append(f"Coordinate dimensions differ")
                consistency_results['is_consistent'] = False

            # Check coordinate values
            for dim in ref_coords:
                if dim in data_coords:
                    if not np.array_equal(ref_coords[dim], data_coords[dim], equal_nan=True):
                        # Check if they're at least close
                        try:
                            if np.allclose(ref_coords[dim], data_coords[dim], equal_nan=True):
                                comparisons.append(f"Coordinates {dim} differ but are close")
                            else:
                                comparisons.append(f"Coordinates {dim} differ significantly")
                                consistency_results['is_consistent'] = False
                        except:
                            comparisons.append(f"Coordinates {dim} differ")
                            consistency_results['is_consistent'] = False

        consistency_results['comparisons'][f"{reference_name}_vs_{name}"] = comparisons

    if consistency_results['is_consistent']:
        logger.info(f"All {len(datasets)} datasets are consistent")
    else:
        logger.warning(f"Dataset consistency check failed: {consistency_results['issues']}")

    return consistency_results


def validate_analysis_parameters(
    parameters: Dict[str, Any],
    required_params: List[str],
    param_types: Optional[Dict[str, type]] = None,
    param_ranges: Optional[Dict[str, Tuple[Any, Any]]] = None
) -> Dict[str, Any]:
    """
    Validate analysis parameters.

    Parameters
    ----------
    parameters : dict
        Analysis parameters to validate
    required_params : list of str
        Required parameter names
    param_types : dict, optional
        Expected types for parameters
    param_ranges : dict, optional
        Valid ranges for parameters (min, max)

    Returns
    -------
    dict
        Validation results
    """
    validation_results = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }

    # Check required parameters
    missing_params = [param for param in required_params if param not in parameters]
    if missing_params:
        validation_results['errors'].append(f"Missing required parameters: {missing_params}")
        validation_results['is_valid'] = False

    # Check parameter types
    if param_types:
        for param_name, expected_type in param_types.items():
            if param_name in parameters:
                param_value = parameters[param_name]
                if not isinstance(param_value, expected_type):
                    validation_results['errors'].append(
                        f"Parameter {param_name}: expected type {expected_type.__name__}, "
                        f"got {type(param_value).__name__}"
                    )
                    validation_results['is_valid'] = False

    # Check parameter ranges
    if param_ranges:
        for param_name, (min_val, max_val) in param_ranges.items():
            if param_name in parameters:
                param_value = parameters[param_name]

                # Handle different types of comparisons
                if isinstance(param_value, (int, float)):
                    if not (min_val <= param_value <= max_val):
                        validation_results['errors'].append(
                            f"Parameter {param_name}: value {param_value} "
                            f"outside range [{min_val}, {max_val}]"
                        )
                        validation_results['is_valid'] = False
                elif isinstance(param_value, str):
                    # For strings, check if in list
                    if isinstance(min_val, list) and param_value not in min_val:
                        validation_results['errors'].append(
                            f"Parameter {param_name}: value '{param_value}' "
                            f"not in allowed values {min_val}"
                        )
                        validation_results['is_valid'] = False

    # Check for unexpected parameters
    allowed_params = set(required_params)
    if param_types:
        allowed_params.update(param_types.keys())
    if param_ranges:
        allowed_params.update(param_ranges.keys())

    unexpected_params = [p for p in parameters.keys() if p not in allowed_params]
    if unexpected_params:
        validation_results['warnings'].append(f"Unexpected parameters: {unexpected_params}")

    if validation_results['is_valid']:
        logger.info("Parameter validation passed")
    else:
        logger.error(f"Parameter validation failed: {validation_results['errors']}")

    return validation_results


def validate_spatial_data(
    data: xr.DataArray,
    required_crs: Optional[str] = None,
    check_bounds: bool = True,
    expected_extent: Optional[Tuple[float, float, float, float]] = None
) -> Dict[str, Any]:
    """
    Validate spatial data.

    Parameters
    ----------
    data : xr.DataArray
        Spatial data to validate
    required_crs : str, optional
        Required coordinate reference system
    check_bounds : bool, optional
        Check if data is within expected bounds
    expected_extent : tuple, optional
        Expected extent (min_lon, min_lat, max_lon, max_lat)

    Returns
    -------
    dict
        Validation results
    """
    validation_results = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }

    # Check for spatial dimensions
    spatial_dims = []
    for dim in ['lon', 'longitude', 'x', 'long']:
        if dim in data.dims:
            spatial_dims.append(dim)
            break

    for dim in ['lat', 'latitude', 'y', 'lat']:
        if dim in data.dims:
            spatial_dims.append(dim)
            break

    if len(spatial_dims) < 2:
        validation_results['errors'].append(
            "Data missing spatial dimensions (need both lon/lat or x/y)"
        )
        validation_results['is_valid'] = False
        return validation_results

    # Check CRS if available and required
    if required_crs and hasattr(data, 'crs'):
        if data.crs != required_crs:
            validation_results['warnings'].append(
                f"CRS mismatch: expected {required_crs}, got {data.crs}"
            )

    # Check bounds
    if check_bounds and expected_extent:
        min_lon, min_lat, max_lon, max_lat = expected_extent

        # Get data extent
        lon_dim = spatial_dims[0]
        lat_dim = spatial_dims[1]

        data_min_lon = float(data[lon_dim].min())
        data_max_lon = float(data[lon_dim].max())
        data_min_lat = float(data[lat_dim].min())
        data_max_lat = float(data[lat_dim].max())

        # Check if data is within expected bounds
        if (data_min_lon < min_lon or data_max_lon > max_lon or
            data_min_lat < min_lat or data_max_lat > max_lat):
            validation_results['warnings'].append(
                f"Data extent [{data_min_lon:.2f}, {data_min_lat:.2f}, "
                f"{data_max_lon:.2f}, {data_max_lat:.2f}] extends beyond "
                f"expected bounds [{min_lon:.2f}, {min_lat:.2f}, "
                f"{max_lon:.2f}, {max_lat:.2f}]"
            )

    # Check coordinate ordering
    if 'lon' in data.dims:
        lon_values = data.lon.values
        if len(lon_values) > 1 and lon_values[0] > lon_values[1]:
            validation_results['warnings'].append(
                "Longitude coordinates appear to be in descending order"
            )

    if 'lat' in data.dims:
        lat_values = data.lat.values
        if len(lat_values) > 1 and lat_values[0] > lat_values[1]:
            validation_results['warnings'].append(
                "Latitude coordinates appear to be in descending order"
            )

    if validation_results['is_valid']:
        logger.info("Spatial data validation passed")
    else:
        logger.error(f"Spatial data validation failed: {validation_results['errors']}")

    return validation_results