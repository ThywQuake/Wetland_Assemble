"""
Loader for GLWD v2. Handles class merging and unit scaling.
"""
import xarray as xr
import rioxarray
from pathlib import Path
from typing import Dict, Union, List
from .base import BaseLoader, standardize_coords
import logging
import glob
import re

logger = logging.getLogger(__name__)

class GLWDLoader(BaseLoader):
    def load(self, info: Dict, **kwargs) -> Union[xr.Dataset, xr.DataArray]:
        """
        Loads GLWD v2.
        Args:
            category (str): Optional. 'ha' or 'pct'. Defaults to 'pct'.
            classes (List[int]): Optional. List of class IDs to load (e.g., [1, 2, 3]). 
                                 If not provided, loads the combined layer if available.
        """
        base_path = Path(info['path'])
        category = kwargs.get('category', 'pct') # default to pct as it's often more useful for area fraction
        classes = kwargs.get('classes', None)
        
        if category not in ['ha', 'pct']:
            raise ValueError("GLWDLoader category must be 'ha' or 'pct'")
            
        subdirectories = info.get('subdirectories', {})
        
        if classes is None:
            # Load combined layer
            combined_dir = base_path / subdirectories.get('combined_classes', 'GLWD_v2_0_combined_classes')
            if category == 'ha':
                file_path = list(combined_dir.glob("*_area_ha_x10.tif"))
                scale_factor = info.get('scale_factor', {}).get('ha', 0.1)
            else:
                file_path = list(combined_dir.glob("*_area_pct.tif"))
                scale_factor = info.get('scale_factor', {}).get('pct', 1.0)
                
            if not file_path:
                 raise FileNotFoundError(f"Combined GLWD TIF not found in {combined_dir}")
            
            logger.info(f"Loading GLWD combined layer: {file_path[0]}")
            da = rioxarray.open_rasterio(file_path[0], chunks=True)
            if da.ndim > 2:
                da = da.squeeze().drop_vars('band', errors='ignore')
                
            if scale_factor != 1.0:
                logger.info(f"Applying scale factor: {scale_factor}")
                da = da * scale_factor
                
            da.name = f"glwd_combined_{category}"
            return standardize_coords(da)
            
        else:
            # Load specific classes and stack them
            sub_dir_key = f"area_by_class_{category}"
            target_dir = base_path / subdirectories.get(sub_dir_key, f"GLWD_v2_0_{sub_dir_key}")
            
            arrays = []
            valid_classes = []
            
            scale_factor = info.get('scale_factor', {}).get(category, 1.0)
            
            for cls_id in classes:
                # E.g., GLWD_v2_0_class_00_ha_x10.tif or GLWD_v2_0_class_00_pct.tif
                pattern = f"GLWD_v2_0_class_{cls_id:02d}_{'ha_x10' if category=='ha' else 'pct'}.tif"
                file_path = target_dir / pattern
                
                if not file_path.exists():
                    logger.warning(f"Class {cls_id} file not found: {file_path}. Skipping.")
                    continue
                    
                da = rioxarray.open_rasterio(file_path, chunks=True)
                if da.ndim > 2:
                     da = da.squeeze().drop_vars('band', errors='ignore')
                
                if scale_factor != 1.0:
                    da = da * scale_factor
                    
                arrays.append(da)
                valid_classes.append(cls_id)
                
            if not arrays:
                 raise FileNotFoundError(f"No valid TIFs found for requested classes {classes} in {target_dir}")
                 
            # Stack along a new 'class' dimension
            stacked = xr.concat(arrays, dim=xr.Variable('class', valid_classes))
            stacked.name = f"glwd_classes_{category}"
            
            return standardize_coords(stacked)
