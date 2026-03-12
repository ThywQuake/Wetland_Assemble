"""
End-to-end analytical pipeline for wetland datasets.
Integrates loader, alignment, mapping, and statistical analysis.
"""

import xarray as xr
import pandas as pd
from typing import List, Optional, Tuple
import logging

from wetland_analysis.data.loader import load_wetland_dataset
from wetland_analysis.data.mappings import get_mapping, COARSE_LABELS
from wetland_analysis.utils.alignment import SpatioTemporalAligner
from wetland_analysis.utils.geospatial import create_30m_grid
from wetland_analysis.analysis.uncertainty import calculate_shannon_entropy
from wetland_analysis.analysis.consensus import calculate_weighted_consensus

logger = logging.getLogger(__name__)

class WetlandEnsemblePipeline:
    """
    Orchestrates the loading, alignment, and analysis of multiple wetland datasets
    to produce consensus and uncertainty maps.
    """
    def __init__(self, roi_bounds: Tuple[float, float, float, float], start_date: str, end_date: str, freq: str = "MS"):
        self.roi = roi_bounds
        self.target_time = pd.date_range(start_date, end_date, freq=freq)
        self.ref_grid = create_30m_grid(self.roi)
        self.aligner = SpatioTemporalAligner(self.ref_grid, target_time_index=self.target_time)
        self.dataset_weights = {}
        
    def add_dataset(self, name: str, weight: float = 1.0, **loader_kwargs):
        """Add a dataset to the pipeline, align it, and assign a reliability weight."""
        logger.info(f"Adding dataset to pipeline: {name}")
        # Note: In a full implementation, we'd load the dataset, apply coarse/fine mapping, 
        # and then pass it to the aligner.
        self.aligner.add_dataset(name, **loader_kwargs)
        self.dataset_weights[name] = weight
        
    def run_analysis(self) -> xr.Dataset:
        """
        Executes the spatial alignment and calculates uncertainty and consensus.
        """
        if not self.aligner.datasets:
            raise ValueError("No datasets added to the pipeline.")
            
        logger.info("Combining aligned datasets...")
        combined_ds = self.aligner.combine()
        
        # Convert combined Dataset to a stacked DataArray for analysis
        data_arrays = [combined_ds[var] for var in combined_ds.data_vars]
        stack = xr.concat(data_arrays, dim="dataset")
        stack = stack.assign_coords(dataset=list(combined_ds.data_vars.keys()))
        
        logger.info("Calculating Shannon Entropy (Uncertainty)...")
        entropy = calculate_shannon_entropy(stack)
        
        logger.info("Calculating Weighted Consensus...")
        weights_list = [self.dataset_weights[name] for name in combined_ds.data_vars.keys()]
        consensus = calculate_weighted_consensus(data_arrays, weights=weights_list)
        
        # Package results
        results = xr.Dataset({
            "consensus_class": consensus,
            "shannon_entropy": entropy
        })
        
        return results
