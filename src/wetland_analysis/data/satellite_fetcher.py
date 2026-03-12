"""
Satellite data fetcher for Google Earth Engine (GEE).
Implements BaseFetcher interface.
"""

import ee
import os
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import logging
from .config import load_gee_config

logger = logging.getLogger(__name__)

class GEEFetcher:
    """
    Fetcher for Sentinel-2 and Landsat-8/9 data from GEE.
    Loads project ID from config/gee_config.yaml or GEE_PROJECT_ID environment variable.
    """
    
    def __init__(self, project_id: Optional[str] = None):
        # 1. User provided ID
        self.project_id = project_id
        
        # 2. Environment variable
        if not self.project_id:
            self.project_id = os.getenv("GEE_PROJECT_ID")
            
        # 3. Config file
        if not self.project_id:
            gee_config = load_gee_config()
            self.project_id = gee_config.get("gee_project_id")
            
        if not self.project_id:
            raise ValueError("GEE Project ID not found. Set 'gee_project_id' in config/gee_config.yaml or 'GEE_PROJECT_ID' environment variable.")
            
        try:
            ee.Initialize(project=self.project_id)
            logger.info(f"GEE Initialized with project: {self.project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize GEE: {e}")
            raise

    def get_sentinel2_image(
        self, 
        roi: ee.Geometry, 
        start_date: str, 
        end_date: str,
        cloud_threshold: float = 0.6
    ) -> ee.Image:
        """
        Fetch a cloud-masked Sentinel-2 median composite using Cloud Score+.
        """
        s2_collection = (
            ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
            .filterBounds(roi)
            .filterDate(start_date, end_date)
        )
        
        # Link Cloud Score+ collection
        cs_plus = ee.ImageCollection("GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED")
        
        def mask_clouds(img):
            # Map CS+ to image
            cs_img = cs_plus.filterBounds(img.geometry()).filterDate(img.date()).first()
            mask = cs_img.select('cs').gt(cloud_threshold)
            return img.updateMask(mask)

        masked_collection = s2_collection.map(mask_clouds)
        
        # Return median composite for the period
        return masked_collection.median().clip(roi)

    def export_to_drive(
        self, 
        image: ee.Image, 
        description: str, 
        folder: str, 
        region: ee.Geometry, 
        scale: int = 30
    ):
        """
        Export GEE image to Google Drive.
        """
        task = ee.batch.Export.image.toDrive(
            image=image.select(['B4', 'B3', 'B2', 'B8']), # RGB + NIR
            description=description,
            folder=folder,
            fileNamePrefix=description,
            region=region,
            scale=scale,
            maxPixels=1e13
        )
        task.start()
        logger.info(f"Export task started: {description}")
        return task
        
    def batch_fetch_hotspots(
        self,
        hotspots: List[Tuple[float, float, float, float]],
        start_date: str,
        end_date: str,
        folder_name: str = "wetland_hotspots",
        cloud_threshold: float = 0.6,
        scale: int = 30
    ) -> List[Any]:
        """
        Fetches Sentinel-2 composites for a list of hotspots and exports them to Drive.
        
        Args:
            hotspots: List of bounding boxes [(min_lon, min_lat, max_lon, max_lat), ...].
            start_date: Start date string (YYYY-MM-DD).
            end_date: End date string (YYYY-MM-DD).
            folder_name: Target folder name in Google Drive.
            cloud_threshold: Threshold for CS+ cloud masking.
            scale: Resolution scale in meters.
            
        Returns:
            List of ee.batch.Task objects that were started.
        """
        tasks = []
        for i, (min_lon, min_lat, max_lon, max_lat) in enumerate(hotspots):
            logger.info(f"Submitting task for hotspot {i+1}/{len(hotspots)}")
            # Convert simple coordinates to ee.Geometry
            roi = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])
            
            # Fetch composite
            image = self.get_sentinel2_image(
                roi=roi,
                start_date=start_date,
                end_date=end_date,
                cloud_threshold=cloud_threshold
            )
            
            # Formulate a unique description based on coordinates
            center_lat = (min_lat + max_lat) / 2.0
            center_lon = (min_lon + max_lon) / 2.0
            desc = f"hotspot_{i:03d}_{center_lat:.4f}_{center_lon:.4f}".replace('.', '_').replace('-', 'm')
            
            # Export
            task = self.export_to_drive(
                image=image,
                description=desc,
                folder=folder_name,
                region=roi,
                scale=scale
            )
            tasks.append(task)
            
        logger.info(f"Successfully submitted {len(tasks)} tasks to GEE.")
        return tasks
