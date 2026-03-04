"""
File I/O utilities for wetland analysis.
"""

import json
import yaml
import pickle
import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any, Dict, Union, Optional
import logging

logger = logging.getLogger(__name__)


def save_results(
    results: Dict[str, Any],
    output_path: Union[str, Path],
    format: str = 'json',
    compress: bool = False
) -> None:
    """
    Save analysis results to file.

    Parameters
    ----------
    results : dict
        Analysis results to save
    output_path : str or Path
        Path to output file
    format : str, optional
        Output format: 'json', 'yaml', 'pickle'
    compress : bool, optional
        Whether to compress the file (for pickle format)
    """
    output_path = Path(output_path)

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if format.lower() == 'json':
            # JSON serialization
            with open(output_path, 'w') as f:
                json.dump(_make_json_serializable(results), f, indent=2)

        elif format.lower() == 'yaml':
            # YAML serialization
            with open(output_path, 'w') as f:
                yaml.dump(_make_json_serializable(results), f, default_flow_style=False)

        elif format.lower() == 'pickle':
            # Pickle serialization
            with open(output_path, 'wb') as f:
                if compress:
                    import gzip
                    with gzip.GzipFile(fileobj=f, mode='wb') as gz:
                        pickle.dump(results, gz, protocol=pickle.HIGHEST_PROTOCOL)
                else:
                    pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)

        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Results saved to {output_path} ({format})")

    except Exception as e:
        logger.error(f"Error saving results to {output_path}: {e}")
        raise


def load_results(
    input_path: Union[str, Path],
    format: str = 'auto'
) -> Dict[str, Any]:
    """
    Load analysis results from file.

    Parameters
    ----------
    input_path : str or Path
        Path to input file
    format : str, optional
        File format: 'json', 'yaml', 'pickle', or 'auto' for automatic detection

    Returns
    -------
    dict
        Loaded results
    """
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Results file not found: {input_path}")

    # Auto-detect format from file extension
    if format == 'auto':
        suffix = input_path.suffix.lower()
        if suffix == '.json':
            format = 'json'
        elif suffix in ['.yaml', '.yml']:
            format = 'yaml'
        elif suffix == '.pkl' or suffix == '.pickle':
            format = 'pickle'
        else:
            raise ValueError(f"Cannot auto-detect format for file: {input_path}")

    try:
        if format.lower() == 'json':
            with open(input_path, 'r') as f:
                results = json.load(f)

        elif format.lower() == 'yaml':
            with open(input_path, 'r') as f:
                results = yaml.safe_load(f)

        elif format.lower() == 'pickle':
            # Check if compressed
            with open(input_path, 'rb') as f:
                # Try to detect gzip compression
                magic_number = f.read(2)
                f.seek(0)

                if magic_number == b'\x1f\x8b':  # Gzip magic number
                    import gzip
                    with gzip.GzipFile(fileobj=f, mode='rb') as gz:
                        results = pickle.load(gz)
                else:
                    results = pickle.load(f)

        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Results loaded from {input_path}")
        return results

    except Exception as e:
        logger.error(f"Error loading results from {input_path}: {e}")
        raise


def _make_json_serializable(obj: Any) -> Any:
    """
    Convert object to JSON-serializable format.

    Parameters
    ----------
    obj : any
        Object to convert

    Returns
    -------
    any
        JSON-serializable object
    """
    if isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_json_serializable(v) for v in obj]
    elif isinstance(obj, tuple):
        return [_make_json_serializable(v) for v in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (xr.DataArray, xr.Dataset)):
        # For xarray objects, extract values and metadata
        result = {
            'type': type(obj).__name__,
            'data': obj.values.tolist() if hasattr(obj, 'values') else None
        }
        if hasattr(obj, 'coords'):
            result['coords'] = {k: v.values.tolist() for k, v in obj.coords.items()}
        if hasattr(obj, 'dims'):
            result['dims'] = list(obj.dims)
        if hasattr(obj, 'attrs'):
            result['attrs'] = dict(obj.attrs)
        return result
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        # Try to convert to string representation
        try:
            return str(obj)
        except:
            logger.warning(f"Could not serialize object of type {type(obj)}")
            return None


def save_dataset(
    dataset: Union[xr.Dataset, xr.DataArray],
    output_path: Union[str, Path],
    format: str = 'netcdf',
    **kwargs
) -> None:
    """
    Save xarray dataset to file.

    Parameters
    ----------
    dataset : xr.Dataset or xr.DataArray
        Dataset to save
    output_path : str or Path
        Path to output file
    format : str, optional
        Output format: 'netcdf', 'zarr', 'geotiff'
    **kwargs : dict
        Additional arguments for the save function
    """
    output_path = Path(output_path)

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if format.lower() == 'netcdf':
            if isinstance(dataset, xr.DataArray):
                dataset = dataset.to_dataset(name='data')
            dataset.to_netcdf(output_path, **kwargs)

        elif format.lower() == 'zarr':
            dataset.to_zarr(output_path, **kwargs)

        elif format.lower() == 'geotiff':
            if isinstance(dataset, xr.DataArray):
                # Requires rioxarray
                import rioxarray
                dataset.rio.to_raster(output_path, **kwargs)
            else:
                raise ValueError("Can only save DataArray to GeoTIFF")

        else:
            raise ValueError(f"Unsupported format for datasets: {format}")

        logger.info(f"Dataset saved to {output_path} ({format})")

    except Exception as e:
        logger.error(f"Error saving dataset to {output_path}: {e}")
        raise


def load_dataset(
    input_path: Union[str, Path],
    format: str = 'auto',
    **kwargs
) -> Union[xr.Dataset, xr.DataArray]:
    """
    Load dataset from file.

    Parameters
    ----------
    input_path : str or Path
        Path to input file
    format : str, optional
        File format: 'netcdf', 'zarr', 'geotiff', or 'auto'
    **kwargs : dict
        Additional arguments for the load function

    Returns
    -------
    xr.Dataset or xr.DataArray
        Loaded dataset
    """
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {input_path}")

    # Auto-detect format from file extension
    if format == 'auto':
        suffix = input_path.suffix.lower()
        if suffix == '.nc' or suffix == '.netcdf':
            format = 'netcdf'
        elif suffix == '.zarr':
            format = 'zarr'
        elif suffix in ['.tif', '.tiff', '.geotiff']:
            format = 'geotiff'
        else:
            raise ValueError(f"Cannot auto-detect format for file: {input_path}")

    try:
        if format.lower() == 'netcdf':
            dataset = xr.open_dataset(input_path, **kwargs)

        elif format.lower() == 'zarr':
            dataset = xr.open_zarr(input_path, **kwargs)

        elif format.lower() == 'geotiff':
            import rioxarray
            dataset = rioxarray.open_rasterio(input_path, **kwargs)
            # Squeeze band dimension if it's 1
            if dataset.shape[0] == 1:
                dataset = dataset.squeeze('band')

        else:
            raise ValueError(f"Unsupported format for datasets: {format}")

        logger.info(f"Dataset loaded from {input_path}")
        return dataset

    except Exception as e:
        logger.error(f"Error loading dataset from {input_path}: {e}")
        raise


def save_figure(
    fig,
    output_path: Union[str, Path],
    dpi: int = 300,
    bbox_inches: str = 'tight',
    **kwargs
) -> None:
    """
    Save matplotlib figure to file.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save
    output_path : str or Path
        Path to output file
    dpi : int, optional
        DPI for saved figure
    bbox_inches : str, optional
        Bounding box inches
    **kwargs : dict
        Additional arguments for savefig
    """
    output_path = Path(output_path)

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        fig.savefig(output_path, dpi=dpi, bbox_inches=bbox_inches, **kwargs)
        logger.info(f"Figure saved to {output_path}")

    except Exception as e:
        logger.error(f"Error saving figure to {output_path}: {e}")
        raise


def get_unique_filename(
    base_path: Union[str, Path],
    suffix: str = '',
    max_attempts: int = 100
) -> Path:
    """
    Get a unique filename by appending numbers if file exists.

    Parameters
    ----------
    base_path : str or Path
        Base file path
    suffix : str, optional
        Suffix to add before extension
    max_attempts : int, optional
        Maximum number of attempts

    Returns
    -------
    Path
        Unique file path
    """
    base_path = Path(base_path)
    base_name = base_path.stem
    extension = base_path.suffix
    directory = base_path.parent

    # Try original name first
    if suffix:
        candidate = directory / f"{base_name}{suffix}{extension}"
    else:
        candidate = directory / f"{base_name}{extension}"

    if not candidate.exists():
        return candidate

    # Try with numbers
    for i in range(1, max_attempts + 1):
        if suffix:
            candidate = directory / f"{base_name}{suffix}_{i}{extension}"
        else:
            candidate = directory / f"{base_name}_{i}{extension}"

        if not candidate.exists():
            return candidate

    # If all attempts fail, raise error
    raise RuntimeError(f"Could not find unique filename after {max_attempts} attempts")