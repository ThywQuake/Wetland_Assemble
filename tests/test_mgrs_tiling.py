import pytest
import numpy as np
from wetland_analysis.utils.mgrs_tiling import GWD30TilingSystem

def test_parse_tile_code():
    ts = GWD30TilingSystem()
    info = ts.parse_tile_code("50TMK")
    assert info["zone"] == 50
    assert info["lat_band"] == "T"
    assert info["hemisphere"] == "N"
    
    info_s = ts.parse_tile_code("01KAA")
    assert info_s["zone"] == 1
    assert info_s["lat_band"] == "K"
    assert info_s["hemisphere"] == "S"

def test_tile_to_extent():
    ts = GWD30TilingSystem()
    # Test a well-known tile: 50TMK (Beijing area)
    # Note: Exact coords will depend on MGRS origin logic implementation
    extent = ts.tile_to_extent("50TMK")
    assert len(extent) == 4
    assert extent[0] < extent[2] # lon_min < lon_max
    assert extent[1] < extent[3] # lat_min < lat_max

def test_gwd30_offset_logic():
    # Verify that the offset is correctly applied in the bounding box calculation
    ts_no_offset = GWD30TilingSystem(offset_x=0, offset_y=0, tile_size_m=100000)
    ts_gwd30 = GWD30TilingSystem(offset_x=-15, offset_y=-15, tile_size_m=109830)
    
    ext_std = ts_no_offset.tile_to_extent("50TMK")
    ext_gwd = ts_gwd30.tile_to_extent("50TMK")
    
    # GWD30 extent should be larger than standard 100km MGRS
    assert (ext_gwd[2] - ext_gwd[0]) > (ext_std[2] - ext_std[0])
