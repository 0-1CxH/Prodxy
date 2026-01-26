#!/usr/bin/env python3

import os
import unittest
import asyncio
from prodxy.graph.mx import ProdxyMxBuilder


class TestProdxyMxBuilderLoadFromYaml(unittest.IsolatedAsyncioTestCase):
    def test_load_from_yaml_complete_config(self):
        # Load the same mock MX config used in the transform test
        yaml_path = os.path.join(os.path.dirname(__file__), "mock_mx_builder_config.yaml")

        # Load using ProdxyMxBuilder.load_from_yaml
        builder = ProdxyMxBuilder.load_from_yaml(yaml_path)

        # Verify that variants were created correctly
        self.assertEqual(len(builder.prodxy_graphs), 3)  # 'a', 'b', '_default'

        # Check variant names
        variant_names = {graph.name for graph in builder.prodxy_graphs}
        self.assertEqual(variant_names, {'a', 'b', '_default'})

        # Verify _default variant has correct number of nodes
        default_graph = next(graph for graph in builder.prodxy_graphs if graph.name == '_default')
        self.assertEqual(len(default_graph.node_configs), 2)

        # Verify 'a' variant has correct number of nodes
        a_graph = next(graph for graph in builder.prodxy_graphs if graph.name == 'a')
        self.assertEqual(len(a_graph.node_configs), 4)

        # Verify 'b' variant has correct number of nodes
        b_graph = next(graph for graph in builder.prodxy_graphs if graph.name == 'b')
        self.assertEqual(len(b_graph.node_configs), 3)

        # Verify start and end node placeholders
        self.assertEqual(default_graph.graph_config.start_node_placeholder, '_start_test')
        self.assertEqual(default_graph.graph_config.end_node_placeholder, '_end')
        self.assertEqual(a_graph.graph_config.start_node_placeholder, '_start_test')
        self.assertEqual(a_graph.graph_config.end_node_placeholder, '_end')
        self.assertEqual(b_graph.graph_config.start_node_placeholder, '_start_test')
        self.assertEqual(b_graph.graph_config.end_node_placeholder, '_end')

        # Verify property library was loaded
        self.assertIsNotNone(builder.property_library)
        self.assertEqual(len(builder.property_library.properties), 2)

        # Verify constraints were loaded
        self.assertEqual(len(builder.property_library.constrains), 1)

        # Verify specific property details
        color_property = next(p for p in builder.property_library.properties if p.property_name == 'color')
        self.assertEqual(len(color_property.categories), 2)

        size_property = next(p for p in builder.property_library.properties if p.property_name == 'size')
        self.assertEqual(len(size_property.categories), 2)

        # for _ in [a_graph, b_graph, default_graph]:
        #     _.compiled_graph.get_graph().print_ascii()
    
    async def test_mx_call(self):
        # Load the mock MX config
        yaml_path = os.path.join(os.path.dirname(__file__), "mock_mx_builder_config.yaml")
        builder = ProdxyMxBuilder.load_from_yaml(yaml_path)

        # Test calling with existing variant 'a'
        graph_a_callable = builder('a')
        self.assertIsNotNone(graph_a_callable)
        self.assertTrue(callable(graph_a_callable))

        # Test calling with existing variant 'b'
        graph_b_callable = builder('b')
        self.assertIsNotNone(graph_b_callable)
        self.assertTrue(callable(graph_b_callable))

        # Test calling with '_default' variant
        default_callable = builder('_default')
        self.assertIsNotNone(default_callable)
        self.assertTrue(callable(default_callable))

        # Test calling with non-existent variant
        non_existent = builder('non_existent')
        self.assertIsNone(non_existent)

        # Test executing variant 'a' with input data
        input_data = {"arg1": "test", "arg2": "test"}
        result_a = await graph_a_callable(input_data)
        self.assertIn("result1", result_a.data)
        self.assertEqual(result_a.data["result1"], True)  # judge:equal should return True
        self.assertIn("result2", result_a.data)
        self.assertEqual(result_a.data["result2"], True)  # judge:equal should return True
        self.assertNotIn("result3", result_a.data)

        # Test executing variant 'b' with input data
        input_data = {"arg2": "test", "arg1": ["test", "other"]}
        result_b = await graph_b_callable(input_data)
        self.assertIn("result1", result_b.data)
        self.assertEqual(result_b.data["result1"], True)  # judge:include should return True
        self.assertNotIn("result2", result_b.data)
        self.assertIn("result3", result_b.data)
        self.assertEqual(result_b.data["result3"], False)


        # Test executing '_default' variant
        input_data = {"arg1": "test", "arg2": ["test", "other"]}
        result_default = await default_callable(input_data)
        self.assertIn("result1", result_default.data)
        self.assertEqual(result_default.data["result1"], False)  # judge:include should return False
        


if __name__ == "__main__":
    unittest.main()