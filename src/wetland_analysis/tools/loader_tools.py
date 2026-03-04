"""
Data loading tools for AI agents.
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def list_datasets() -> Dict:
    """
    List all available wetland datasets.

    Returns:
        Dictionary with list of available datasets
    """
    from ..data.loader import list_available_datasets, load_dataset_config

    try:
        datasets = list_available_datasets()
        config = load_dataset_config()

        # Get summary info for each dataset
        dataset_summaries = []
        for ds_name in datasets:
            ds_info = config.get('datasets', {}).get(ds_name, {})
            dataset_summaries.append({
                'name': ds_name,
                'display_name': ds_info.get('name', ds_name),
                'type': ds_info.get('type', 'unknown'),
                'format': ds_info.get('format', 'unknown'),
                'resolution': ds_info.get('resolution', 'unknown')
            })

        return {
            'success': True,
            'datasets': dataset_summaries,
            'count': len(dataset_summaries)
        }
    except Exception as e:
        logger.error(f"Error listing datasets: {e}")
        return {
            'success': False,
            'error': str(e),
            'datasets': []
        }


def get_dataset_info(dataset_name: str) -> Dict:
    """
    Get detailed information about a specific dataset.

    Args:
        dataset_name: Name of the dataset

    Returns:
        Dictionary with dataset information
    """
    from ..data.loader import get_dataset_info as _get_info

    try:
        info = _get_info(dataset_name)
        return {
            'success': True,
            'dataset': info
        }
    except ValueError as e:
        # Dataset not found
        available = list_datasets()
        return {
            'success': False,
            'error': str(e),
            'available_datasets': [ds['name'] for ds in available.get('datasets', [])]
        }
    except Exception as e:
        logger.error(f"Error getting dataset info: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def load_dataset(
    dataset_name: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    region: Optional[str] = None
) -> Dict:
    """
    Load a wetland dataset for analysis.

    Args:
        dataset_name: Name of the dataset to load
        year: Year for annual/monthly datasets
        month: Month for monthly datasets (1-12)
        region: Region to clip data to

    Returns:
        Dictionary with loaded data info or error
    """
    from ..data.loader import load_wetland_dataset
    from ..data.preprocessing import mask_region
    from ..data.config import get_region_bbox

    try:
        # Load the dataset
        logger.info(f"Loading dataset: {dataset_name} (year={year}, month={month})")
        data = load_wetland_dataset(
            dataset_name=dataset_name,
            year=year,
            month=month
        )

        # Apply region mask if specified
        if region:
            try:
                bbox = get_region_bbox(region)
                data = mask_region(data, bbox)
                logger.info(f"Applied region mask: {region}")
            except ValueError:
                logger.warning(f"Region '{region}' not found, ignoring")

        # Get summary statistics
        summary = {
            'shape': data.shape if hasattr(data, 'shape') else None,
            'dims': list(data.dims) if hasattr(data, 'dims') else None,
            'variables': list(data.data_vars) if hasattr(data, 'data_vars') else None
        }

        # Add coordinate info
        if hasattr(data, 'coords'):
            coord_info = {}
            for coord in data.coords:
                coord_info[coord] = {
                    'size': data.coords[coord].size,
                    'min': float(data.coords[coord].min()) if data.coords[coord].size > 0 else None,
                    'max': float(data.coords[coord].max()) if data.coords[coord].size > 0 else None
                }
            summary['coordinates'] = coord_info

        return {
            'success': True,
            'dataset_name': dataset_name,
            'year': year,
            'month': month,
            'region': region,
            'summary': summary,
            'data_loaded': True
        }

    except ValueError as e:
        # Configuration error (e.g., path not set)
        return {
            'success': False,
            'error': str(e),
            'hint': 'Dataset path may not be configured. Please update config/datasets.yaml with actual data paths.'
        }
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        return {
            'success': False,
            'error': str(e)
        }