"""
Wetland Classification Mapping Dictionary.

This module provides unified concordance maps for various global wetland
datasets, supporting both coarse and fine-grained classification schemes.

Consensus Classes (Coarse):
    0: Non-wetland
    1: Permanent Water
    2: Forested Wetland
    3: Non-forested Wetland

Consensus Classes (Fine-grained):
    0: Non-wetland
    1: Open Water
    2: Mangrove (Coastal Forested)
    3: Peatland (Forested or Non-forested peat-forming)
    4: Forested Swamp (Non-peat forested)
    5: Marsh (Non-forested, non-peat)
    6: Floodplain (Seasonally inundated)
    7: Coastal Wetland (Non-mangrove tidal/coastal)
"""

from typing import Dict, Any

# Coarse-grained Concordance Map (Original 4 classes)
COARSE_CONCORDANCE_MAP: Dict[str, Dict[int, int]] = {
    "GWD30": {
        0: 0, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 14: 1,
        9: 2, 12: 2,
        8: 3, 10: 3, 11: 3, 13: 3
    },
    "GLWD": {
        0: 0, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 30: 1,
        8: 2, 10: 2, 12: 2, 14: 2, 16: 2, 18: 2, 20: 2, 22: 2, 24: 2, 26: 2, 28: 2,
        9: 3, 11: 3, 13: 3, 15: 3, 17: 3, 19: 3, 21: 3, 23: 3, 25: 3, 27: 3, 29: 3, 31: 3, 32: 3, 33: 3
    },
    "G2017": {
        0: 0, 10: 1, 20: 2, 30: 2,
        40: 3, 50: 3, 60: 3, 70: 3, 80: 3, 90: 3, 100: 3
    }
}

# Fine-grained Concordance Map (8 classes)
FINE_CONCORDANCE_MAP: Dict[str, Dict[int, int]] = {
    "GWD30": {
        0: 0,                           # Non-wetland
        1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 14: 1, # Open Water
        12: 2,                          # Coastal Swamp -> Mangrove
        9: 4,                           # Inland Swamp -> Forested Swamp
        8: 5,                           # Inland Marsh -> Marsh
        10: 6,                          # Floodplain -> Floodplain
        11: 7, 13: 7                    # Coastal Marsh/Tidal Flat -> Coastal Wetland
    },
    "GLWD": {
        0: 0,                           # Dryland
        1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 30: 1, # Water
        28: 2,                          # Mangrove -> Mangrove
        22: 3, 23: 3, 24: 3, 25: 3, 26: 3, 27: 3, # Boreal/Temp/Trop Peatland -> Peatland
        8: 4, 10: 4, 12: 4, 14: 4, 16: 4, 18: 4, 20: 4, # Forested categories -> Forested Swamp
        9: 5, 11: 5, 13: 5, 15: 5, 17: 5, 19: 5, 21: 5, 33: 5, # Non-forested/Rice -> Marsh
        29: 7, 31: 7, 32: 7             # Saltmarsh/Coastal -> Coastal Wetland
        # Note: GLWD doesn't have a direct 'Floodplain' class in the same way GWD30 does, 
        # but 'regularly flooded' riverine (10, 11) could be considered. 
        # Here we keep them in Swamp/Marsh for consistency unless further specified.
    },
    "G2017": {
        0: 0,                           # No Data
        10: 1,                          # Open Water
        20: 2,                          # Mangrove -> Mangrove
        # G2017 Peatland is usually a separate mask, but Swamp (30) often implies peat in CIFOR.
        # Without the peat mask, 30 is Forested Swamp.
        30: 4,                          # Swamps -> Forested Swamp
        40: 5, 50: 5, 80: 5, 90: 5, 100: 5, # Fens/Marshes -> Marsh
        60: 6, 70: 6                    # Floodplains -> Floodplain
    }
}

COARSE_LABELS: Dict[int, str] = {
    0: "Non-wetland",
    1: "Permanent Water",
    2: "Forested Wetland",
    3: "Non-forested Wetland"
}

FINE_LABELS: Dict[int, str] = {
    0: "Non-wetland",
    1: "Open Water",
    2: "Mangrove",
    3: "Peatland",
    4: "Forested Swamp",
    5: "Marsh",
    6: "Floodplain",
    7: "Coastal Wetland"
}

def get_mapping(dataset_name: str, level: str = "coarse") -> Dict[int, int]:
    """
    Retrieve the mapping dictionary for a specific dataset.
    
    Args:
        dataset_name: Name of the dataset (e.g., 'GWD30', 'GLWD', 'G2017')
        level: 'coarse' (4 classes) or 'fine' (8 classes)
    """
    name = dataset_name.upper()
    if level == "coarse":
        if name not in COARSE_CONCORDANCE_MAP:
            raise ValueError(f"Coarse mapping for '{dataset_name}' not found.")
        return COARSE_CONCORDANCE_MAP[name]
    elif level == "fine":
        if name not in FINE_CONCORDANCE_MAP:
            raise ValueError(f"Fine mapping for '{dataset_name}' not found.")
        return FINE_CONCORDANCE_MAP[name]
    else:
        raise ValueError("Level must be 'coarse' or 'fine'.")

def get_labels(level: str = "coarse") -> Dict[int, str]:
    """Get labels for the specified classification level."""
    return COARSE_LABELS if level == "coarse" else FINE_LABELS
