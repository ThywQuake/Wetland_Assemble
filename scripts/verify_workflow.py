"""
Workflow verification script to ensure all modules are correctly implemented 
and the environment is ready for server-side execution.
"""

import sys
import os
from pathlib import Path

# Ensure src is in PYTHONPATH
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

def check_environment():
    print("--- 1. Checking Environment ---")
    libs = ["xarray", "rioxarray", "ee", "pyproj", "shapely", "numpy", "dask"]
    missing = []
    for lib in libs:
        try:
            __import__(lib)
            print(f"[OK] {lib} is installed.")
        except ImportError:
            print(f"[MISSING] {lib} is NOT installed.")
            missing.append(lib)
    return missing

def verify_tiling():
    print("\n--- 2. Verifying GWD30 Tiling Logic ---")
    from wetland_analysis.utils.mgrs_tiling import GWD30TilingSystem
    ts = GWD30TilingSystem()
    
    # Test point_to_tile
    lat, lon = 39.9, 116.4 # Beijing
    tile = ts.point_to_tile(lat, lon)
    print(f"Point ({lat}, {lon}) -> Tile: {tile}")
    
    # Test tile_to_extent
    extent = ts.tile_to_extent(tile)
    print(f"Tile {tile} -> Extent (W, S, E, N): {extent}")
    
    # Test bbox
    tiles = ts.bbox_to_tiles(39.8, 116.3, 40.0, 116.5)
    print(f"BBox Tiles: {tiles}")
    
    return True

def verify_uncertainty():
    print("\n--- 3. Verifying Uncertainty & Consensus ---")
    import xarray as xr
    import numpy as np
    from wetland_analysis.analysis.uncertainty import calculate_shannon_entropy
    from wetland_analysis.analysis.consensus import calculate_weighted_consensus

    # Mock stack (dataset, lat, lon)
    data = np.array([
        [[1, 1], [0, 1]], # DS 1
        [[1, 0], [1, 1]]  # DS 2
    ])
    stack = xr.DataArray(data, dims=["dataset", "lat", "lon"])
    
    entropy = calculate_shannon_entropy(stack)
    print(f"Entropy mean: {entropy.mean().values:.4f}")
    
    consensus = calculate_weighted_consensus([stack.isel(dataset=0), stack.isel(dataset=1)])
    print(f"Consensus mean: {consensus.mean().values:.4f}")
    
    return True

def check_gee():
    print("\n--- 4. Checking GEE Connection ---")
    if not os.getenv("GEE_PROJECT_ID"):
        print("[SKIP] GEE_PROJECT_ID not set. Skipping GEE smoke test.")
        return
    
    from wetland_analysis.data.satellite_fetcher import GEEFetcher
    try:
        fetcher = GEEFetcher()
        print("[OK] GEE Authentication successful.")
    except Exception as e:
        print(f"[ERROR] GEE Initialization failed: {e}")

if __name__ == "__main__":
    missing = check_environment()
    if not missing:
        verify_tiling()
        verify_uncertainty()
        check_gee()
        print("\nVerification Complete.")
    else:
        print(f"\nPlease install missing libs: pip install {' '.join(missing)}")
