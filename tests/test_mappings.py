import unittest
from wetland_analysis.data.mappings import get_mapping, WETLAND_CONCORDANCE_MAP, CONSENSUS_LABELS

class TestMappings(unittest.TestCase):
    def test_gwd30_mapping(self):
        mapping = get_mapping("GWD30")
        self.assertEqual(mapping[0], 0)  # Non-wetland
        self.assertEqual(mapping[3], 1)  # Lake -> Water
        self.assertEqual(mapping[9], 2)  # Swamp -> Forested
        self.assertEqual(mapping[8], 3)  # Marsh -> Non-forested

    def test_glwd_mapping(self):
        mapping = get_mapping("GLWD")
        self.assertEqual(mapping[1], 1)   # Lake -> Water
        self.assertEqual(mapping[28], 2)  # Mangrove -> Forested
        self.assertEqual(mapping[33], 3)  # Rice paddies -> Non-forested

    def test_g2017_mapping(self):
        mapping = get_mapping("G2017")
        self.assertEqual(mapping[10], 1)  # Open Water
        self.assertEqual(mapping[30], 2)  # Swamps -> Forested
        self.assertEqual(mapping[80], 3)  # Marshes -> Non-forested

    def test_invalid_dataset(self):
        with self.assertRaises(ValueError):
            get_mapping("UNKNOWN")

    def test_labels(self):
        self.assertEqual(CONSENSUS_LABELS[1], "Permanent Water")
        self.assertEqual(CONSENSUS_LABELS[2], "Forested Wetland")

if __name__ == "__main__":
    unittest.main()
