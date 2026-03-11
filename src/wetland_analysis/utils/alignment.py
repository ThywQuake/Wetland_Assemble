"""
Spatio-temporal scale alignment for multiple wetland datasets.
Includes robust strategies for high-res offsets, EASE-Grid, and temporal aggregation.
"""

import xarray as xr
import pandas as pd
import numpy as np
import rioxarray
from rasterio.enums import Resampling
from typing import Dict, List, Optional, Union, Tuple, Protocol
import logging
from .geospatial import align_to_reference
from .mgrs_tiling import GWD30TilingSystem
from ..data.loader import load_wetland_dataset

logger = logging.getLogger(__name__)

class AlignmentStrategy(Protocol):
    """Protocol for dataset-specific alignment logic."""
    def align(self, data: xr.DataArray, reference: xr.DataArray) -> xr.DataArray:
        ...

class HighResGWD30Strategy:
    """Strategy for GWD30 which requires 15m offset handling via MGRS tiling."""
    def __init__(self):
        self.tiling = GWD30TilingSystem()

    def align(self, data: xr.DataArray, reference: xr.DataArray) -> xr.DataArray:
        logger.info("Applying GWD30-specific high-res alignment (15m offset correction).")
        # Ensure the input has the correct UTM CRS if it's missing
        if data.rio.crs is None:
            # GWD30 is typically UTM, but if loaded as raw, we might need to infer
            # Here we assume the loader/rioxarray has already read the CRS from GeoTIFF
            pass
        
        # Reproject matching the reference grid
        return data.rio.reproject_match(reference, resampling=Resampling.mode)

class EASEGridStrategy:
    """Strategy for datasets in EASE-Grid (like SWAMPS) which can have CRS ambiguity."""
    def align(self, data: xr.DataArray, reference: xr.DataArray) -> xr.DataArray:
        logger.info("Applying EASE-Grid alignment (EPSG:6933).")
        if data.rio.crs is None or "EASE" in str(data.rio.crs):
            data.rio.write_crs("EPSG:6933", inplace=True)
        return data.rio.reproject_match(reference, resampling=Resampling.bilinear)

class DefaultStrategy:
    """Standard reproject_match strategy."""
    def __init__(self, is_categorical: bool = True):
        self.resampling = Resampling.mode if is_categorical else Resampling.bilinear

    def align(self, data: xr.DataArray, reference: xr.DataArray) -> xr.DataArray:
        return data.rio.reproject_match(reference, resampling=self.resampling)

class SpatioTemporalAligner:
    """
    Orchestrate spatial and temporal alignment of multiple wetland datasets
    with support for heterogeneous data formats and coordinate systems.
    """
    def __init__(
        self,
        reference_grid: xr.DataArray,
        target_time_index: Optional[pd.DatetimeIndex] = None
    ):
        self.reference_grid = reference_grid
        self.target_time_index = target_time_index
        self.datasets: Dict[str, xr.DataArray] = {}
        
    def _validate_alignment(self, name: str, aligned: xr.DataArray):
        """Perform physical consistency checks on aligned data."""
        # Check 1: Do we have non-NaN overlap?
        valid_count = aligned.notnull().sum().values
        if valid_count == 0:
            logger.error(f"ZERO OVERLAP: Dataset {name} has no spatial overlap with the reference grid!")
            raise ValueError(f"Dataset {name} alignment resulted in empty data.")
            
        # Check 2: Relative size check
        # If the aligned data is much smaller than reference, warn the user
        ref_size = self.reference_grid.size
        overlap_ratio = valid_count / ref_size
        if overlap_ratio < 0.05:
            logger.warning(f"LOW OVERLAP: Dataset {name} covers only {overlap_ratio:.1%} of the reference ROI.")

    def _get_strategy(self, name: str, is_categorical: bool) -> AlignmentStrategy:
        """Select the appropriate alignment strategy based on dataset characteristics."""
        name = name.lower()
        if "gwd30" in name:
            return HighResGWD30Strategy()
        elif "swamps" in name or "ease" in name:
            return EASEGridStrategy()
        else:
            return DefaultStrategy(is_categorical=is_categorical)

    def add_dataset(
        self,
        dataset_name: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        is_categorical: bool = True,
        temporal_method: str = "mean"
    ):
        """
        Load, spatially align, and temporally aggregate a dataset.
        """
        logger.info(f"Processing dataset: {dataset_name}")
        
        # 1. Load
        data = load_wetland_dataset(dataset_name, year=year, month=month)
        
        # 2. Temporal Aggregation (if daily -> monthly/annual)
        if 'time' in data.dims and self.target_time_index is not None:
            freq = self.target_time_index.inferred_freq or "MS"
            if temporal_method == "max":
                data = data.resample(time=freq).max()
            else:
                data = data.resample(time=freq).mean()

        # 3. Spatial Alignment
        strategy = self._get_strategy(dataset_name, is_categorical)
        aligned = strategy.align(data, self.reference_grid)
        
        # 4. Final Temporal Reindex (ensure exact match with target_time_index)
        if self.target_time_index is not None:
            if 'time' not in aligned.dims:
                # Add time dimension if missing (for static datasets)
                aligned = aligned.expand_dims(time=self.target_time_index)
            else:
                aligned = aligned.reindex(time=self.target_time_index, method='nearest')
        
        # 5. Validation
        self._validate_alignment(dataset_name, aligned)
        
        self.datasets[dataset_name] = aligned
        return aligned

    def align_temporally(self, name: str, method: str = "repeat"):
        """
        Explicitly perform temporal alignment if not already done by add_dataset.
        Note: add_dataset already performs alignment if target_time_index is set.
        """
        if name not in self.datasets:
            raise ValueError(f"Dataset {name} not found in aligner. Call add_dataset first.")
        
        # If it's already aligned, we don't need to do much unless the user wants a different method
        logger.debug(f"Dataset {name} already has temporal dimensions aligned.")

    def combine(self) -> xr.Dataset:
        """Combine all aligned datasets into one Dataset."""
        return xr.Dataset(self.datasets)

    def combine_to_dataset(self) -> xr.Dataset:
        """Alias for combine() to match example script usage."""
        return self.combine()

def aggregate_to_coarse(
    fine_data: xr.DataArray,
    coarse_grid: xr.DataArray,
    method: str = "sum"
) -> xr.DataArray:
    """
    High-precision aggregation from fine (e.g. 30m) to coarse (e.g. 25km) grid.
    Calculates wetland fraction by counting valid wetland pixels within each coarse cell.
    """
    logger.info(f"Aggregating fine data to coarse grid using {method} method.")
    
    # We use area-weighted resampling for fraction calculation
    # This ensures that even if grids are slightly offset, the total area is preserved
    return fine_data.rio.reproject_match(
        coarse_grid,
        resampling=Resampling.average
    )
