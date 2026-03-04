"""
Satellite data fetcher for Google Earth Engine (GEE).
Implements BaseFetcher interface.
"""

import ee
import os
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class GEEFetcher:
    """
    Fetcher for Sentinel-2 and Landsat-8/9 data from GEE.
    Requires GEE_PROJECT_ID environment variable.
    """
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GEE_PROJECT_ID")
        if not self.project_id:
            raise ValueError("GEE_PROJECT_ID must be set.")
            
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
