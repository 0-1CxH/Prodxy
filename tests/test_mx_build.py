#!/usr/bin/env python3

import os
import unittest
from prodxy.graph.mx import ProdxyMxBuilder


class TestProdxyMxBuilderLoadFromYaml(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()