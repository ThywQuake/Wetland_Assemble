"""
HotspotAnalyzer module for finding regions of high disagreement in wetland ensembles.
Optimized for Dask array processing.
"""
import xarray as xr
import numpy as np
import dask.array as da
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class HotspotAnalyzer:
    """
    Identifies high-uncertainty hotspots from spatial entropy maps.
    Designed to work with Dask-backed xarray datasets.
    """
    def __init__(self, window_size_deg: float = 0.1):
        """
        Args:
            window_size_deg (float): The size of the search window in degrees (approx 10km for 0.1 deg).
        """
        self.window_size_deg = window_size_deg

    def find_top_n_hotspots(
        self, 
        entropy_da: xr.DataArray, 
        n: int = 5,
        resolution_deg: float = 0.0002777777777777778 # Approx 30m in degrees
    ) -> List[Tuple[float, float, float, float]]:
        """
        Finds the top N bounding boxes with the highest mean Shannon Entropy.
        
        Args:
            entropy_da: xarray DataArray containing shannon_entropy. Must have 'lat' and 'lon' dimensions.
            n: Number of hotspots to return.
            resolution_deg: Grid resolution in degrees to convert window_size_deg to pixels.
            
        Returns:
            List of bounding boxes: [(min_lon, min_lat, max_lon, max_lat), ...]
        """
        if 'lat' not in entropy_da.dims or 'lon' not in entropy_da.dims:
            raise ValueError("DataArray must have 'lat' and 'lon' dimensions.")

        window_pixels = max(1, int(self.window_size_deg / resolution_deg))
        logger.info(f"Using window size of {window_pixels}x{window_pixels} pixels.")

        # Handle potentially empty or all-NaN arrays
        if entropy_da.isnull().all().compute():
            logger.warning("Entropy array is entirely null. Returning empty hotspots.")
            return []

        # 1. Coarsen the array to find block means. 
        # Using coarsen is much more memory efficient than rolling windows for non-overlapping block search.
        logger.info("Coarsening entropy map to find regional means...")
        
        # We need to make sure the dimensions are perfectly divisible by the window, or drop the edges.
        # Boundary='trim' handles the edges if they don't divide perfectly.
        coarsened = entropy_da.coarsen(
            lat=window_pixels, 
            lon=window_pixels, 
            boundary='trim'
        ).mean()

        # 2. Compute the result if it's a Dask array. We assume the coarsened array is small enough to fit in memory.
        logger.info("Computing coarsened array...")
        coarsened_computed = coarsened.compute()
        
        # 3. Flatten and sort to find top N indices
        # Replace NaNs with -inf so they sort to the bottom
        flat_vals = np.nan_to_num(coarsened_computed.values.flatten(), nan=-np.inf)
        
        # Get indices of top N
        # argsort is ascending, so we take the last N and reverse
        top_n_flat_indices = np.argsort(flat_vals)[-n:][::-1]
        
        # Filter out indices that had -inf (which means they were all NaNs)
        valid_indices = [idx for idx in top_n_flat_indices if flat_vals[idx] != -np.inf]
        
        # 4. Reconstruct bounding boxes
        hotspots = []
        shape = coarsened_computed.shape
        
        for flat_idx in valid_indices:
            # Convert flat index back to 2D indices of the coarsened array
            lat_idx, lon_idx = np.unravel_index(flat_idx, shape)
            
            # Get the center coordinates of this coarse block
            center_lat = float(coarsened_computed.lat.values[lat_idx])
            center_lon = float(coarsened_computed.lon.values[lon_idx])
            
            # Reconstruct the original bounding box based on the window size
            half_window = self.window_size_deg / 2.0
            min_lon = center_lon - half_window
            max_lon = center_lon + half_window
            # Note: lat usually decreases as index increases, but we just use center +/- half_window
            min_lat = center_lat - half_window
            max_lat = center_lat + half_window
            
            hotspots.append((min_lon, min_lat, max_lon, max_lat))
            
        logger.info(f"Identified {len(hotspots)} valid hotspots.")
        return hotspots
