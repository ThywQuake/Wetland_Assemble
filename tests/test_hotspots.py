import pytest
import xarray as xr
import numpy as np
from wetland_analysis.analysis.hotspots import HotspotAnalyzer

def test_hotspot_analyzer_basic():
    # Create a dummy dataset
    lat = np.linspace(10, 11, 100)
    lon = np.linspace(20, 21, 100)
    
    # Create random data, but put a high value region in the middle
    data = np.random.rand(100, 100)
    data[40:60, 40:60] = 5.0 # High entropy hotspot
    
    da = xr.DataArray(data, coords=[lat, lon], dims=['lat', 'lon'], name='shannon_entropy')
    
    analyzer = HotspotAnalyzer(window_size_deg=0.1) # approx 10x10 pixels with this grid
    
    # Needs to match resolution roughly
    resolution = lat[1] - lat[0]
    
    hotspots = analyzer.find_top_n_hotspots(da, n=3, resolution_deg=resolution)
    
    assert len(hotspots) == 3
    # The first hotspot should be near the center (lat ~10.5, lon ~20.5)
    min_lon, min_lat, max_lon, max_lat = hotspots[0]
    
    assert 20.4 < min_lon < 20.6
    assert 10.4 < min_lat < 10.6

def test_hotspot_analyzer_all_nan():
    lat = np.linspace(10, 11, 10)
    lon = np.linspace(20, 21, 10)
    data = np.full((10, 10), np.nan)
    da = xr.DataArray(data, coords=[lat, lon], dims=['lat', 'lon'])
    
    analyzer = HotspotAnalyzer()
    hotspots = analyzer.find_top_n_hotspots(da)
    assert len(hotspots) == 0
