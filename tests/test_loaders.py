import pytest
import xarray as xr
import numpy as np
from pathlib import Path
from wetland_analysis.data.loaders import (
    BaseLoader, GeoTIFFLoader, NetCDFLoader, GWD30Loader, 
    GLWDLoader, TOPMODELLoader, SWAMPSLoader, BerkeleyLoader
)

# A mock for standardizing coords to make sure it doesn't fail
def test_standardize_coords():
    from wetland_analysis.data.loaders import standardize_coords
    
    da = xr.DataArray(np.random.rand(10, 10), dims=['latitude', 'longitude'], coords={'latitude': np.arange(10), 'longitude': np.arange(10)})
    std_da = standardize_coords(da)
    assert 'lat' in std_da.dims
    assert 'lon' in std_da.dims
    assert 'latitude' not in std_da.dims

# Just testing registry instantiation
def test_loader_registry():
    from wetland_analysis.data.loader import _REGISTRY
    
    assert isinstance(_REGISTRY.get_loader('gwd30'), GWD30Loader)
    assert isinstance(_REGISTRY.get_loader('glwd'), GLWDLoader)
    assert isinstance(_REGISTRY.get_loader('topmodel'), TOPMODELLoader)
    assert isinstance(_REGISTRY.get_loader('swamps'), SWAMPSLoader)
    assert isinstance(_REGISTRY.get_loader('berkeley'), BerkeleyLoader)
    assert isinstance(_REGISTRY.get_loader('netcdf'), NetCDFLoader)
    assert isinstance(_REGISTRY.get_loader('geotiff'), GeoTIFFLoader)
    
    with pytest.raises(ValueError):
        _REGISTRY.get_loader('unknown_loader')

