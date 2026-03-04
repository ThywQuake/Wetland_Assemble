"""
Functions for calculating ensemble uncertainty and spatial consistency.
"""

import xarray as xr
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def calculate_shannon_entropy(
    stacked_datasets: xr.DataArray,
    dim: str = "dataset"
) -> xr.DataArray:
    """
    Calculate normalized Shannon Entropy across multiple datasets.
    
    H = -sum(p_i * log_b(p_i)) / log_b(n)
    where p_i is the probability of class i (wetland or non-wetland).
    
    Parameters
    ----------
    stacked_datasets : xr.DataArray
        Binary datasets (0 or 1) stacked along the 'dataset' dimension.
    dim : str, default 'dataset'
        Dimension along which to calculate entropy.
        
    Returns
    -------
    xr.DataArray
        Normalized Shannon Entropy (0 to 1).
    """
    n_datasets = stacked_datasets.sizes[dim]
    
    # Calculate probability of wetland (class 1)
    p1 = stacked_datasets.mean(dim=dim)
    p0 = 1.0 - p1
    
    # Avoid log(0)
    p1 = p1.where(p1 > 0, 1e-10)
    p0 = p0.where(p0 > 0, 1e-10)
    
    # Shannon Entropy formula
    entropy = -(p1 * np.log2(p1) + p0 * np.log2(p0))
    
    # Normalize by log2(2) since we have 2 classes (binary)
    # H_norm = entropy / log2(2) = entropy
    
    return entropy

def calculate_confusion_index(
    stacked_datasets: xr.DataArray,
    dim: str = "dataset"
) -> xr.DataArray:
    """
    Calculate the Confusion Index (CI) for binary ensemble.
    CI = 1 - (p_max1 - p_max2)
    For binary cases, p_max1 is max(p_wetland, p_non_wetland), 
    p_max2 is min(p_wetland, p_non_wetland).
    
    Parameters
    ----------
    stacked_datasets : xr.DataArray
        Binary datasets (0 or 1) stacked along the 'dataset' dimension.
        
    Returns
    -------
    xr.DataArray
        Confusion Index (0 to 1).
    """
    p1 = stacked_datasets.mean(dim=dim)
    p0 = 1.0 - p1
    
    p_max1 = xr.where(p1 >= p0, p1, p0)
    p_max2 = xr.where(p1 < p0, p1, p0)
    
    ci = 1.0 - (p_max1 - p_max2)
    return ci

def identify_uncertainty_hotspots(
    entropy: xr.DataArray,
    threshold: float = 0.8
) -> xr.DataArray:
    """
    Identify areas where datasets have high disagreement.
    """
    return entropy > threshold
