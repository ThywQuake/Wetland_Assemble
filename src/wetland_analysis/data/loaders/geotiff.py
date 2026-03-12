"""
Generic GeoTIFF loader.
"""
import xarray as xr
import rioxarray
from pathlib import Path
from typing import Dict, Union
from .base import BaseLoader, standardize_coords
import logging

logger = logging.getLogger(__name__)

class GeoTIFFLoader(BaseLoader):
    def load(self, info: Dict, **kwargs) -> Union[xr.Dataset, xr.DataArray]:
        base_path = Path(info['path'])
        
        # Simple file fallback matching what we had
        if 'files' in info:
            file_key = 'wetland' if 'wetland' in info['files'] else list(info['files'].keys())[0]
            file_path = str(base_path / info['files'][file_key])
        else:
            files = list(base_path.glob("*.tif"))
            if not files:
                raise FileNotFoundError(f"No TIFF files found in {base_path}. Fix Suggestion: Verify path in config/datasets.yaml")
            file_path = str(files[0])
            
        logger.info(f"Loading GeoTIFF: {file_path}")
        da = rioxarray.open_rasterio(file_path, chunks=True)
        if da.ndim > 2:
            da = da.squeeze()
            
        return standardize_coords(da)
