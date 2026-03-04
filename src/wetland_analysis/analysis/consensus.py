"""
Ensemble methods for creating multi-source wetland consensus maps.
"""

import xarray as xr
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def calculate_weighted_consensus(
    datasets: List[xr.DataArray],
    weights: Optional[List[float]] = None
) -> xr.DataArray:
    """
    Combine multiple binary wetland maps into a weighted consensus map.
    
    Parameters
    ----------
    datasets : List[xr.DataArray]
        List of aligned binary (0/1) DataArrays.
    weights : List[float], optional
        Weights for each dataset. If None, equal weights are used.
        
    Returns
    -------
    xr.DataArray
        Consensus map (values from 0 to sum(weights)).
    """
    if weights is None:
        weights = [1.0] * len(datasets)
    
    if len(datasets) != len(weights):
        raise ValueError("Number of datasets and weights must match.")
        
    # Initialize consensus with the first weighted dataset
    consensus = datasets[0] * weights[0]
    
    for ds, w in zip(datasets[1:], weights[1:]):
        consensus += ds * w
        
    consensus.name = "wetland_consensus"
    return consensus

def get_binary_consensus(
    consensus: xr.DataArray,
    threshold: float
) -> xr.DataArray:
    """
    Binarize a consensus map based on a confidence threshold.
    Example: threshold=0.5 means >50% of weight must agree.
    """
    return (consensus >= threshold).astype(np.uint8)
