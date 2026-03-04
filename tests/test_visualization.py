import pytest
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from wetland_analysis.visualization.comparison import (
    plot_spatial_agreement,
    plot_multiscale_comparison,
    plot_uncertainty_heatmap,
    plot_temporal_comparison
)

@pytest.fixture
def mock_data_30m():
    lons = np.linspace(0, 1, 100)
    lats = np.linspace(0, 1, 100)
    data = np.random.randint(0, 2, size=(100, 100))
    return xr.DataArray(data, coords=[('lat', lats), ('lon', lons)], name='wetland')

@pytest.fixture
def mock_data_low():
    lons = np.linspace(0, 1, 10)
    lats = np.linspace(0, 1, 10)
    data = np.random.randint(0, 2, size=(10, 10))
    return xr.DataArray(data, coords=[('lat', lats), ('lon', lons)], name='wetland_low')

def test_plot_spatial_agreement(mock_data_30m):
    # Mock aligned data
    ds_a = mock_data_30m
    ds_b = mock_data_30m
    fig = plot_spatial_agreement(ds_a, ds_b)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_multiscale_comparison(mock_data_30m, mock_data_low):
    fig = plot_multiscale_comparison(mock_data_30m, mock_data_low, coarsen_factor=10)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_uncertainty_heatmap(mock_data_30m):
    entropy = mock_data_30m.astype(float) # Mock entropy
    fig = plot_uncertainty_heatmap(entropy)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_temporal_comparison():
    times = np.array(['2020-01-01', '2020-02-01'], dtype='datetime64')
    data = np.random.rand(2, 5, 5)
    ds = xr.DataArray(data, coords=[('time', times), ('lat', np.arange(5)), ('lon', np.arange(5))], name='test')
    fig = plot_temporal_comparison([ds], names=['Dataset1'])
    assert isinstance(fig, plt.Figure)
    plt.close(fig)
