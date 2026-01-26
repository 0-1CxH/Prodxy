import os
import unittest
import asyncio
from prodxy.graph.builder import ProdxyGraph, ProdxyNodeConfig, ProdxyOperationConfig, ProdxyGraphConfig


class TestMinimalGraphBuild(unittest.IsolatedAsyncioTestCase):

    async def test_graph_execution(self):
        """Test the minimal graph execution functionality"""
        graph = ProdxyGraph(
            ProdxyGraphConfig(
                node_configs=[
                    ProdxyNodeConfig(
                        name="node1",
                        operations=[
                            ProdxyOperationConfig(
                                main_op_name="judge:equal",
                                condition_op_name="condition:exist",
                                read_paths={
                                    "target": "$.arg1",
                                    "source": "$.arg2"
                                },
                                write_path="$.result1"
                            )
                        ],
                        conditions={
                            True: "node2",
                            False: "node3",
                        },
                    ),
                    ProdxyNodeConfig(
                        name="node2",
                        operations=[
                            ProdxyOperationConfig(
                                main_op_name="judge:equal",
                                condition_op_name="condition:exist",
                                read_paths={
                                    "target": "$.arg1",
                                    "source": "$.arg2"
                                },
                                write_path="$.result2"
                            )
                        ]
                    ),
                    ProdxyNodeConfig(
                        name="node3",
                        operations=[
                            ProdxyOperationConfig(
                                main_op_name="judge:equal",
                                condition_op_name="condition:exist",
                                read_paths={
                                    "target": "$.arg1",
                                    "source": "$.arg2"
                                },
                                write_path="$.result3"
                            )
                        ]
                    ),
                ]
            )
        )

        # Test graph structure
        graph_structure = graph.compiled_graph.get_graph()
        self.assertIsNotNone(graph_structure)

        # Test graph execution
        result = await graph({
            "arg1": 1,
            "arg2": 2,
        })

        # Verify result structure
        self.assertIsNotNone(result)
        self.assertIn("data", result.__dict__)
        self.assertIn("condition_signal", result.__dict__)
        self.assertIn("prodxy_trace", result.__dict__)

        # Verify data is present
        self.assertIn("arg1", result.data)
        self.assertIn("arg2", result.data)

        # Verify trace is populated
        self.assertIsInstance(result.prodxy_trace, list)
        self.assertEqual(len(result.prodxy_trace), 2)

        # assert result
        self.assertEqual(result.data["result1"], False)
        self.assertNotIn("result2", result.data)
        self.assertEqual(result.data["result3"], False)

    def test_graph_structure_visualization(self):
        """Test that the graph can be visualized (ASCII representation)"""
        graph = ProdxyGraph.from_dict(
            {
                "node_configs": [
                    {
                        "name": "node1",
                        "operations": [
                            {
                                "main_op_name": "judge:equal",
                                "condition_op_name": "condition:exist",
                                "read_paths": {
                                    "target": "$.arg1",
                                    "source": "$.arg2"
                                },
                                "write_path": "$.result1"
                            }
                        ],
                        "conditions": {
                            True: "node2",
                            False: "node3",
                        },
                    },
                    {
                        "name": "node2",
                        "operations": [
                            {
                                "main_op_name": "judge:equal",
                                "condition_op_name": "condition:exist",
                                "read_paths": {
                                    "target": "$.arg1",
                                    "source": "$.arg2"
                                },
                                "write_path": "$.result2"
                            }
                        ]
                    },
                    {
                        "name": "node3",
                        "operations": [
                            {
                                "main_op_name": "judge:equal",
                                "condition_op_name": "condition:exist",
                                "read_paths": {
                                    "target": "$.arg1",
                                    "source": "$.arg2"
                                },
                                "write_path": "$.result3"
                            },
                        ],
                        "conditions": {
                            1: "node2",
                            2: "node4",
                            3: "node5",
                        },
                    },
                    {
                        "name": "node4",
                        "operations": [
                            {
                                "main_op_name": "judge:equal",
                                "condition_op_name": "condition:exist",
                                "read_paths": {
                                    "target": "$.arg1",
                                    "source": "$.arg2"
                                },
                                "write_path": "$.result4"
                            }
                        ]
                    },
                    {
                        "name": "node5",
                        "operations": [
                            {
                                "main_op_name": "judge:equal",
                                "condition_op_name": "condition:exist",
                                "read_paths": {
                                    "target": "$.arg1",
                                    "source": "$.arg2"
                                },
                                "write_path": "$.result5"
                            }
                        ],
                        "conditions": {
                            1: "_end",
                            2: "node2"
                        }
                    },
                ]
            }
        )

        # Test that ASCII representation can be generated
        # This is mainly to ensure the graph structure is valid
        try:
            graph.compiled_graph.get_graph().draw_ascii()
        except Exception as e:
            print(f"Graph ASCII visualization failed: {e}")
    
    def test_graph_load_yaml(self):
        graph = ProdxyGraph.from_yaml(
            os.path.join(os.path.dirname(__file__), "mock_builder_config.yaml")
        )
        self.assertIsNotNone(graph)


if __name__ == "__main__":
    unittest.main()