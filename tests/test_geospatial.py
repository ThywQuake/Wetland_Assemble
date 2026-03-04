import pytest
import xarray as xr
import numpy as np
import rioxarray
from wetland_analysis.utils.geospatial import align_to_reference, create_30m_grid

def test_align_to_reference():
    # Create a low-res dataset (1 degree)
    lons = np.arange(0, 5, 1)
    lats = np.arange(5, 0, -1)
    data = np.random.rand(5, 5)
    ds_low = xr.DataArray(
        data,
        coords=[lats, lons],
        dims=["lat", "lon"],
        name="test_data"
    ).rio.write_crs("EPSG:4326")

    # Create a high-res reference grid (0.5 degree)
    lons_hi = np.arange(0, 5, 0.5)
    lats_hi = np.arange(5, 0, -0.5)
    ref_grid = xr.DataArray(
        np.zeros((10, 10)),
        coords=[lats_hi, lons_hi],
        dims=["lat", "lon"]
    ).rio.write_crs("EPSG:4326")

    # Align
    aligned = align_to_reference(ds_low, ref_grid)

    assert aligned.shape == (10, 10)
    assert aligned.rio.crs == ref_grid.rio.crs
    assert np.allclose(aligned.lon, ref_grid.lon)

def test_create_30m_grid():
    bounds = (0, 0, 0.01, 0.01) # west, south, east, north
    grid = create_30m_grid(bounds)
    
    assert "lat" in grid.dims
    assert "lon" in grid.dims
    assert grid.rio.crs.to_string() == "EPSG:4326"
