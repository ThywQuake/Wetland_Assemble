"""
Data loading and preprocessing module for wetland datasets.
"""

from .loader import load_wetland_dataset, list_available_datasets
from .config import load_dataset_config, get_dataset_path
from .preprocessing import resample_to_common_grid, mask_region
from .mappings import get_mapping, WETLAND_CONCORDANCE_MAP, CONSENSUS_LABELS

__all__ = [
    "load_wetland_dataset",
    "list_available_datasets",
    "load_dataset_config",
    "get_dataset_path",
    "resample_to_common_grid",
    "mask_region",
    "get_mapping",
    "WETLAND_CONCORDANCE_MAP",
    "CONSENSUS_LABELS",
]