"""
Initialization of loaders.
"""
from .base import BaseLoader, standardize_coords
from .geotiff import GeoTIFFLoader
from .netcdf import NetCDFLoader
from .gwd30 import GWD30Loader
from .glwd import GLWDLoader
from .topmodel import TOPMODELLoader
from .swamps import SWAMPSLoader
from .berkeley import BerkeleyLoader

__all__ = [
    'BaseLoader',
    'standardize_coords',
    'GeoTIFFLoader',
    'NetCDFLoader',
    'GWD30Loader',
    'GLWDLoader',
    'TOPMODELLoader',
    'SWAMPSLoader',
    'BerkeleyLoader'
]
