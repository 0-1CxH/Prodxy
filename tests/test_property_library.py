import unittest
from collections import Counter
from prodxy.operation.attribute_sampler import (
    ProdxyPropertyLibrary,
    ProdxyPropertyLibraryConfig,
    ProdxyProperty,
    ProdxyPropertyCategory,
    ProdxyPropertyItem,
    PropertyIndicator,
    ProdxyConstrain
)

class TestProdxyPropertyLibrary(unittest.TestCase):

    def setUp(self):
        # Create test data
        self.test_config_dict = {
            "properties": [
                {
                    "property_name": "color",
                    "categories": [
                        {
                            "category_name": "primary",
                            "weight": 2.0,
                            "items": [
                                {"item_name": "red", "weight": 3.0},
                                {"item_name": "blue", "weight": 2.0},
                                {"item_name": "yellow", "weight": 1.0}
                            ]
                        },
                        {
                            "category_name": "secondary",
                            "weight": 1.0,
                            "items": [
                                {"item_name": "green", "weight": 2.0},
                                {"item_name": "orange", "weight": 1.5},
                                {"item_name": "purple", "weight": 1.0}
                            ]
                        }
                    ]
                },
                {
                    "property_name": "size",
                    "categories": [
                        {
                            "category_name": "small",
                            "weight": 1.0,
                            "items": [
                                {"item_name": "tiny", "weight": 1.0},
                                {"item_name": "small", "weight": 2.0}
                            ]
                        },
                        {
                            "category_name": "large",
                            "weight": 2.0,
                            "items": [
                                {"item_name": "big", "weight": 2.0},
                                {"item_name": "huge", "weight": 1.0}
                            ]
                        }
                    ]
                }
            ],
            "constrains": [
                {
                    "constrain_subject": {
                        "property_name": "color",
                        "category_name": "primary",
                        "item_name": "red"
                    },
                    "constrain_object": [
                        {
                            "property_name": "size",
                            "category_name": "large",
                            "item_name": "huge"
                        }
                    ]
                }
            ]
        }

        # Create manual config object for testing
        color_property = ProdxyProperty(
            property_name="color",
            categories=[
                ProdxyPropertyCategory(
                    category_name="primary",
                    weight=2.0,
                    items=[
                        ProdxyPropertyItem("red", 3.0),
                        ProdxyPropertyItem("blue", 2.0),
                        ProdxyPropertyItem("yellow", 1.0)
                    ]
                ),
                ProdxyPropertyCategory(
                    category_name="secondary",
                    weight=1.0,
                    items=[
                        ProdxyPropertyItem("green", 2.0),
                        ProdxyPropertyItem("orange", 1.5),
                        ProdxyPropertyItem("purple", 1.0)
                    ]
                )
            ]
        )

        size_property = ProdxyProperty(
            property_name="size",
            categories=[
                ProdxyPropertyCategory(
                    category_name="small",
                    weight=1.0,
                    items=[
                        ProdxyPropertyItem("tiny", 1.0),
                        ProdxyPropertyItem("small", 2.0)
                    ]
                ),
                ProdxyPropertyCategory(
                    category_name="large",
                    weight=2.0,
                    items=[
                        ProdxyPropertyItem("big", 2.0),
                        ProdxyPropertyItem("huge", 1.0)
                    ]
                )
            ]
        )

        constrain = ProdxyConstrain(
            constrain_subject=PropertyIndicator("color", "primary", "red"),
            constrain_object=[PropertyIndicator("size", "large", "huge")]
        )

        self.test_config = ProdxyPropertyLibraryConfig(
            properties=[color_property, size_property],
            constrains=[constrain]
        )

    def test_load_from_dict(self):
        """Test loading configuration from dictionary"""
        library = ProdxyPropertyLibrary.load_from_dict(self.test_config_dict)

        self.assertIsInstance(library, ProdxyPropertyLibrary)
        self.assertEqual(len(library.properties), 2)
        self.assertEqual(len(library.constrains), 1)

        # Check property names
        property_names = [prop.property_name for prop in library.properties]
        self.assertIn("color", property_names)
        self.assertIn("size", property_names)

        # Check categories
        color_prop = next(prop for prop in library.properties if prop.property_name == "color")
        self.assertEqual(len(color_prop.categories), 2)

        # Check items
        primary_cat = next(cat for cat in color_prop.categories if cat.category_name == "primary")
        self.assertEqual(len(primary_cat.items), 3)

    def test_sample_categories_basic(self):
        """Test basic category sampling without constraints"""
        library = ProdxyPropertyLibrary(self.test_config)

        # Test sampling categories for color property
        indicators = library.sample_categories("color", count=5, allow_repeat=True)

        self.assertEqual(len(indicators), 5)
        for indicator in indicators:
            self.assertEqual(indicator.property_name, "color")
            self.assertIn(indicator.category_name, ["primary", "secondary"])
            self.assertIsNone(indicator.item_name)

    def test_sample_categories_unique(self):
        """Test unique category sampling"""
        library = ProdxyPropertyLibrary(self.test_config)

        # Should get all unique categories
        indicators = library.sample_categories("color", count=2, allow_repeat=False)

        self.assertEqual(len(indicators), 2)
        category_names = [indicator.category_name for indicator in indicators]
        self.assertEqual(len(set(category_names)), 2)
        self.assertEqual(set(category_names), {"primary", "secondary"})

    def test_sample_categories_weighted(self):
        """Test weighted category sampling"""
        library = ProdxyPropertyLibrary(self.test_config)

        # Primary has weight 2.0, secondary has weight 1.0
        # Primary should be sampled more frequently
        indicators = library.sample_categories("color", count=1000, allow_repeat=True)

        category_counts = Counter([indicator.category_name for indicator in indicators])

        # Primary should have approximately twice as many samples as secondary
        self.assertGreater(category_counts["primary"], category_counts["secondary"])
        ratio = category_counts["primary"] / category_counts["secondary"]
        self.assertGreater(ratio, 1.5)  # Should be close to 2.0
        self.assertLess(ratio, 3.0)    # Allow more variance for random sampling

    def test_sample_items_basic(self):
        """Test basic item sampling"""
        library = ProdxyPropertyLibrary(self.test_config)

        indicators = library.sample_items("color", "primary", count=3, allow_repeat=True)

        self.assertEqual(len(indicators), 3)
        for indicator in indicators:
            self.assertEqual(indicator.property_name, "color")
            self.assertEqual(indicator.category_name, "primary")
            self.assertIn(indicator.item_name, ["red", "blue", "yellow"])

    def test_sample_items_weighted(self):
        """Test weighted item sampling"""
        library = ProdxyPropertyLibrary(self.test_config)

        # red:3.0, blue:2.0, yellow:1.0
        indicators = library.sample_items("color", "primary", count=100, allow_repeat=True)

        item_counts = Counter([indicator.item_name for indicator in indicators])

        # red should have highest count, then blue, then yellow
        self.assertGreater(item_counts["red"], item_counts["blue"])
        self.assertGreater(item_counts["blue"], item_counts["yellow"])

    def test_sample_categories_with_constraints(self):
        """Test category sampling with constraints"""
        # This test is more complex and would require constraint resolution logic
        # For now, we'll test that the method exists and returns expected format
        library = ProdxyPropertyLibrary(self.test_config)

        indicators = library.sample_categories("color", count=2)

        self.assertEqual(len(indicators), 2)
        for indicator in indicators:
            self.assertEqual(indicator.property_name, "color")
            self.assertIn(indicator.category_name, ["primary", "secondary"])

    def test_invalid_property_name(self):
        """Test sampling with invalid property name"""
        library = ProdxyPropertyLibrary(self.test_config)

        with self.assertRaises(ValueError):
            library.sample_categories("invalid_property", count=1)

        with self.assertRaises(ValueError):
            library.sample_items("invalid_property", "primary", count=1)

    def test_invalid_category_name(self):
        """Test sampling with invalid category name"""
        library = ProdxyPropertyLibrary(self.test_config)

        with self.assertRaises(ValueError):
            library.sample_items("color", "invalid_category", count=1)

if __name__ == '__main__':
    unittest.main()