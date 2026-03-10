"""
Wetland Classification Mapping Dictionary.

This module provides a unified concordance map for various global wetland
datasets, mapping their unique classification systems into a consensus 4-class
standard for spatial comparison and validation.

Consensus Classes:
    0: Non-wetland
    1: Permanent Water (Lakes, Rivers, Reservoirs)
    2: Forested Wetland (Swamps, Peat forests, Mangroves)
    3: Non-forested Wetland (Marshes, Fens, Floodplains, Wet meadows)
"""

from typing import Dict, List, Union

# Core Concordance Map
WETLAND_CONCORDANCE_MAP: Dict[str, Dict[int, int]] = {
    # Global Wetland Dataset 30m (Annual)
    "GWD30": {
        0: 0,   # Non-wetland
        1: 1,   # River
        2: 1,   # Canal/Channel
        3: 1,   # Lake
        4: 1,   # Reservoir/Pond
        5: 1,   # Estuary Water
        6: 1,   # Lagoon
        7: 1,   # Aquaculture Pond / Salt Pan
        8: 3,   # Inland Marsh -> Non-forested
        9: 2,   # Inland Swamp -> Forested
        10: 3,  # Floodplain -> Non-forested
        11: 3,  # Coastal Marsh -> Non-forested
        12: 2,  # Coastal Swamp -> Forested
        13: 3,  # Tidal Flat -> Non-forested
        14: 1,  # Shallow Marine Water -> Water
    },
    
    # Global Lakes and Wetlands Database v2
    "GLWD": {
        0: 0,   # Dryland
        1: 1,   # Freshwater lake
        2: 1,   # Saline lake
        3: 1,   # Reservoir
        4: 1,   # Large river
        5: 1,   # Large estuarine river
        6: 1,   # Other permanent waterbody
        7: 1,   # Small streams
        8: 2,   # Lacustrine, forested -> Forested
        9: 3,   # Lacustrine, non-forested -> Non-forested
        10: 2,  # Riverine, regularly flooded, forested -> Forested
        11: 3,  # Riverine, regularly flooded, non-forested -> Non-forested
        12: 2,  # Riverine, seasonally flooded, forested -> Forested
        13: 3,  # Riverine, seasonally flooded, non-forested -> Non-forested
        14: 2,  # Riverine, seasonally saturated, forested -> Forested
        15: 3,  # Riverine, seasonally saturated, non-forested -> Non-forested
        16: 2,  # Palustrine, regularly flooded, forested -> Forested
        17: 3,  # Palustrine, regularly flooded, non-forested -> Non-forested
        18: 2,  # Palustrine, seasonally saturated, forested -> Forested
        19: 3,  # Palustrine, seasonally saturated, non-forested -> Non-forested
        20: 2,  # Ephemeral, forested -> Forested
        21: 3,  # Ephemeral, non-forested -> Non-forested
        22: 2,  # Arctic/boreal peatland, forested -> Forested
        23: 3,  # Arctic/boreal peatland, non-forested -> Non-forested
        24: 2,  # Temperate peatland, forested -> Forested
        25: 3,  # Temperate peatland, non-forested -> Non-forested
        26: 2,  # Tropical/subtropical peatland, forested -> Forested
        27: 3,  # Tropical/subtropical peatland, non-forested -> Non-forested
        28: 2,  # Mangrove -> Forested
        29: 3,  # Saltmarsh -> Non-forested
        30: 1,  # Large river delta -> Water (often complex, mapping to water as conservative)
        31: 3,  # Other coastal wetland -> Non-forested
        32: 3,  # Salt pan, saline/brackish wetland -> Non-forested
        33: 3,  # Rice paddies -> Non-forested (human-made)
    },

    # G2017 (Cifor Tropical/Subtropical Wetland)
    "G2017": {
        0: 0,   # No Data / Dryland
        10: 1,  # Open Water
        20: 2,  # Mangrove -> Forested
        30: 2,  # Swamps (Incl. bogs) -> Forested
        40: 3,  # Fens -> Non-forested
        50: 3,  # Riverine and Lacustrine -> Non-forested
        60: 3,  # Floodplains -> Non-forested
        70: 3,  # Floodplains -> Non-forested
        80: 3,  # Marshes -> Non-forested
        90: 3,  # Marshes -> Non-forested
        100: 3, # Marshes -> Non-forested
    }
}

CONSENSUS_LABELS: Dict[int, str] = {
    0: "Non-wetland",
    1: "Permanent Water",
    2: "Forested Wetland",
    3: "Non-forested Wetland"
}

def get_mapping(dataset_name: str) -> Dict[int, int]:
    """Retrieve the mapping dictionary for a specific dataset."""
    name = dataset_name.upper()
    if name not in WETLAND_CONCORDANCE_MAP:
        raise ValueError(f"Mapping for dataset '{dataset_name}' not found.")
    return WETLAND_CONCORDANCE_MAP[name]
