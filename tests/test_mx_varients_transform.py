#!/usr/bin/env python3

import os
import yaml
import unittest
from prodxy.graph.mx import transform_mx_config_to_standard


class TestTransformMXConfig(unittest.TestCase):
    def test_transform_mx_config(self):
        # Test with the mock MX config
        with open(os.path.join(os.path.dirname(__file__), "mock_mx_builder_config.yaml"), 'r') as f:
            mx_config = yaml.safe_load(f)

        result = transform_mx_config_to_standard(mx_config['mx_node_configs'])

        # Verify we have 'a' and 'b' variants
        self.assertIn('a', result)
        self.assertIn('b', result)

        # Verify structure of 'a' variant
        a_config = result['a']
        self.assertEqual(len(a_config), 4)

        # Check first node in 'a' variant
        node1_a = a_config[0]
        self.assertEqual(node1_a['name'], 'node1')
        self.assertIn('operations', node1_a)
        self.assertIn('conditions', node1_a)
        self.assertEqual(node1_a['conditions'][True], 'node2')
        self.assertEqual(node1_a['conditions'][False], 'node3')

        # Verify structure of 'b' variant
        b_config = result['b']
        self.assertEqual(len(b_config), 3)

        # Check first node in 'b' variant
        node1_b = b_config[0]
        self.assertEqual(node1_b['name'], 'node1')
        self.assertIn('operations', node1_b)
        self.assertIn('conditions', node1_b)
        self.assertEqual(node1_b['conditions'][True], 'node3')
        self.assertEqual(node1_b['conditions'][False], 'node2')

        # Verify structure of '_default' variant
        default_config = result['_default']
        self.assertEqual(len(default_config), 2)

        # Check first node in '_default' variant
        node1_default = default_config[0]
        self.assertEqual(node1_default['name'], 'node1')
        self.assertIn('operations', node1_default)
        self.assertIn('conditions', node1_default)
        self.assertEqual(node1_default['conditions'][True], '_end')
        self.assertEqual(node1_default['conditions'][False], 'node2')


if __name__ == "__main__":
    unittest.main()