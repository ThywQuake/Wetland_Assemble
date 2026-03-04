"""
Tests for data loading module.
"""

import pytest
import numpy as np
import xarray as xr
from pathlib import Path
import tempfile
import yaml

from src.wetland_analysis.data.loader import (
    load_dataset_config,
    list_available_datasets,
    get_dataset_info,
    validate_dataset_loaded
)


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    config = {
        'datasets': {
            'test_dataset': {
                'name': 'Test Dataset',
                'type': 'test',
                'format': 'netcdf',
                'path': '/test/path',
                'file': 'test.nc'
            }
        },
        'regions': {
            'global': {
                'name': 'Global',
                'bbox': [-180, -90, 180, 90]
            }
        },
        'analysis': {
            'spatial_metrics': ['OA', 'Kappa']
        }
    }

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        config_path = f.name

    yield config_path

    # Cleanup
    Path(config_path).unlink()


@pytest.fixture
def sample_netcdf_data():
    """Create sample NetCDF data for testing."""
    # Create a simple xarray Dataset
    data = xr.Dataset(
        {
            'wetland': (['lat', 'lon'], np.random.rand(10, 20))
        },
        coords={
            'lat': np.linspace(-90, 90, 10),
            'lon': np.linspace(-180, 180, 20)
        }
    )

    # Write to temporary file
    with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as f:
        data.to_netcdf(f.name)
        file_path = f.name

    yield file_path, data

    # Cleanup
    Path(file_path).unlink()


def test_load_dataset_config(sample_config):
    """Test loading dataset configuration."""
    # Monkey patch the config path
    import src.wetland_analysis.data.loader as loader_module
    original_path = loader_module._CONFIG_PATH
    loader_module._CONFIG_PATH = Path(sample_config)

    try:
        config = load_dataset_config()

        assert 'datasets' in config
        assert 'test_dataset' in config['datasets']
        assert config['datasets']['test_dataset']['name'] == 'Test Dataset'
        assert 'regions' in config
        assert 'analysis' in config

    finally:
        # Restore original path
        loader_module._CONFIG_PATH = original_path


def test_list_available_datasets(sample_config):
    """Test listing available datasets."""
    import src.wetland_analysis.data.loader as loader_module
    original_path = loader_module._CONFIG_PATH
    loader_module._CONFIG_PATH = Path(sample_config)

    try:
        datasets = list_available_datasets()
        assert isinstance(datasets, list)
        assert 'test_dataset' in datasets

    finally:
        loader_module._CONFIG_PATH = original_path


def test_get_dataset_info(sample_config):
    """Test getting dataset information."""
    import src.wetland_analysis.data.loader as loader_module
    original_path = loader_module._CONFIG_PATH
    loader_module._CONFIG_PATH = Path(sample_config)

    try:
        info = get_dataset_info('test_dataset')
        assert info['name'] == 'Test Dataset'
        assert info['type'] == 'test'
        assert info['format'] == 'netcdf'

        # Test error for non-existent dataset
        with pytest.raises(ValueError, match='Dataset.*not found'):
            get_dataset_info('non_existent_dataset')

    finally:
        loader_module._CONFIG_PATH = original_path


def test_validate_dataset_loaded():
    """Test dataset validation."""
    # Test with valid DataArray
    data = xr.DataArray(
        np.random.rand(10, 10),
        dims=['lat', 'lon']
    )
    assert validate_dataset_loaded(data, 'test_dataset') is True

    # Test with empty DataArray
    empty_data = xr.DataArray(np.array([]))
    assert validate_dataset_loaded(empty_data, 'test_dataset') is False

    # Test with Dataset
    dataset = xr.Dataset({'var1': (['x', 'y'], np.random.rand(5, 5))})
    assert validate_dataset_loaded(dataset, 'test_dataset') is True

    # Test with empty Dataset
    empty_dataset = xr.Dataset()
    assert validate_dataset_loaded(empty_dataset, 'test_dataset') is False


def test_load_wetland_dataset_missing_config():
    """Test loading dataset with missing configuration."""
    from src.wetland_analysis.data.loader import load_wetland_dataset

    # Should raise error when config doesn't exist
    with pytest.raises(FileNotFoundError):
        load_wetland_dataset('test_dataset')


# Note: More comprehensive tests for actual data loading would require
# actual data files or more sophisticated mocking. These are covered
# in integration tests.


if __name__ == '__main__':
    pytest.main([__file__, '-v'])