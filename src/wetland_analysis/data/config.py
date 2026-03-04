"""
Configuration management for wetland datasets.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "datasets.yaml"


def load_dataset_config() -> Dict:
    """Load the main dataset configuration file."""
    if not _CONFIG_PATH.exists():
        logger.warning(f"Configuration file not found at {_CONFIG_PATH}")
        return {"datasets": {}, "regions": {}, "analysis": {}}

    with open(_CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)

    return config


def get_dataset_path(dataset_name: str) -> str:
    """Get the filesystem path for a dataset."""
    config = load_dataset_config()
    datasets = config.get('datasets', {})

    if dataset_name not in datasets:
        raise ValueError(f"Dataset '{dataset_name}' not found in configuration")

    return datasets[dataset_name].get('path', '')


def get_region_bbox(region_name: str) -> List[float]:
    """Get bounding box for a region."""
    config = load_dataset_config()
    regions = config.get('regions', {})

    if region_name not in regions:
        raise ValueError(f"Region '{region_name}' not found in configuration")

    return regions[region_name].get('bbox', [-180, -90, 180, 90])


def get_analysis_parameters() -> Dict:
    """Get analysis parameters from configuration."""
    config = load_dataset_config()
    return config.get('analysis', {})


def update_dataset_path(dataset_name: str, new_path: str) -> None:
    """
    Update dataset path in configuration.

    Parameters
    ----------
    dataset_name : str
        Name of the dataset to update
    new_path : str
        New filesystem path
    """
    config = load_dataset_config()

    if dataset_name not in config.get('datasets', {}):
        raise ValueError(f"Dataset '{dataset_name}' not found in configuration")

    config['datasets'][dataset_name]['path'] = new_path

    # Save updated configuration
    with open(_CONFIG_PATH, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    logger.info(f"Updated path for dataset '{dataset_name}' to: {new_path}")


def validate_config() -> List[str]:
    """
    Validate configuration file.

    Returns
    -------
    list of str
        List of validation errors, empty if valid
    """
    errors = []

    try:
        config = load_dataset_config()
    except Exception as e:
        errors.append(f"Failed to load configuration: {e}")
        return errors

    # Check required sections
    if 'datasets' not in config:
        errors.append("Missing 'datasets' section in configuration")
        return errors

    # Validate each dataset
    for dataset_name, dataset_info in config['datasets'].items():
        if not isinstance(dataset_info, dict):
            errors.append(f"Dataset '{dataset_name}' configuration is not a dictionary")
            continue

        # Check required fields
        required_fields = ['name', 'type', 'format']
        for field in required_fields:
            if field not in dataset_info:
                errors.append(f"Dataset '{dataset_name}' missing required field: '{field}'")

        # Check path configuration
        path = dataset_info.get('path', '')
        if not path or path == '/path/to/data/':
            errors.append(f"Dataset '{dataset_name}' has unconfigured path. Please update config/datasets.yaml")

    # Validate regions if present
    if 'regions' in config:
        for region_name, region_info in config['regions'].items():
            if not isinstance(region_info, dict):
                errors.append(f"Region '{region_name}' configuration is not a dictionary")
                continue

            if 'bbox' not in region_info:
                errors.append(f"Region '{region_name}' missing 'bbox' field")
            else:
                bbox = region_info['bbox']
                if not isinstance(bbox, list) or len(bbox) != 4:
                    errors.append(f"Region '{region_name}' bbox must be a list of 4 numbers")

    return errors