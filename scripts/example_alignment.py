"""
Usage example for Spatio-Temporal Alignment.
"""

import pandas as pd
import xarray as xr
from wetland_analysis.utils.alignment import SpatioTemporalAligner
from wetland_analysis.utils.geospatial import create_30m_grid

def example_alignment():
    # 1. Define ROI and Reference Grid (Amazon region example)
    roi_bounds = (-65.0, -3.0, -64.0, -2.0)  # [west, south, east, north]
    ref_grid = create_30m_grid(roi_bounds)
    
    # 2. Define Target Time Index (Year 2018 monthly)
    target_time = pd.date_range("2018-01-01", "2018-12-01", freq="MS")
    
    # 3. Initialize Aligner
    aligner = SpatioTemporalAligner(ref_grid, target_time_index=target_time)
    
    try:
        # 4. Add Datasets
        # Load GWD30 for 2018 and align spatially
        aligner.add_dataset("gwd30", year=2018)
        
        # Load GLWD (static) and align spatially
        aligner.add_dataset("glwd_v2")
        
        # 5. Temporal Alignment
        # Repeat GLWD across the 12 months
        aligner.align_temporally("glwd_v2", method="repeat")
        
        # Repeat GWD30 (annual) across the 12 months
        aligner.align_temporally("gwd30", method="repeat")
        
        # 6. Combine
        combined_ds = aligner.combine_to_dataset()
        print("Successfully combined datasets:")
        print(combined_ds)
        
    except Exception as e:
        print(f"Alignment failed: {e}")
        print("Note: Ensure data paths in config/datasets.yaml are updated.")

if __name__ == "__main__":
    example_alignment()
