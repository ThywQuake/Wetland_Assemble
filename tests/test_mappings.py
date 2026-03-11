import unittest
from wetland_analysis.data.mappings import (
    get_mapping, 
    COARSE_LABELS, 
    FINE_LABELS, 
    CONSENSUS_LABELS, 
    WETLAND_CONCORDANCE_MAP
)

class TestMappings(unittest.TestCase):
    def test_gwd30_mapping(self):
        mapping = get_mapping("GWD30", level="coarse")
        self.assertEqual(mapping[0], 0)  # Non-wetland
        self.assertEqual(mapping[3], 1)  # Lake -> Water
        self.assertEqual(mapping[9], 2)  # Swamp -> Forested
        self.assertEqual(mapping[8], 3)  # Marsh -> Non-forested

    def test_legacy_aliases(self):
        self.assertEqual(CONSENSUS_LABELS, COARSE_LABELS)
        self.assertEqual(WETLAND_CONCORDANCE_MAP["GWD30"][0], 0)

    def test_glwd_mapping(self):
        mapping = get_mapping("GLWD", level="coarse")
        self.assertEqual(mapping[1], 1)   # Lake -> Water
        self.assertEqual(mapping[28], 2)  # Mangrove -> Forested
        self.assertEqual(mapping[33], 3)  # Rice paddies -> Non-forested

    def test_g2017_mapping(self):
        mapping = get_mapping("G2017", level="coarse")
        self.assertEqual(mapping[10], 1)  # Open Water
        self.assertEqual(mapping[30], 2)  # Swamps -> Forested
        self.assertEqual(mapping[80], 3)  # Marshes -> Non-forested

    def test_invalid_dataset(self):
        with self.assertRaises(ValueError):
            get_mapping("UNKNOWN")

    def test_labels(self):
        self.assertEqual(COARSE_LABELS[1], "Permanent Water")
        self.assertEqual(COARSE_LABELS[2], "Forested Wetland")
        self.assertEqual(FINE_LABELS[2], "Mangrove")

if __name__ == "__main__":
    unittest.main()
