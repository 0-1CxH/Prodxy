import unittest
from prodxy.graph.builer import ProdxyGraph, ProdxyNodeConfig, ProdxyOperationConfig


class TestMinimalGraphBuild(unittest.TestCase):

    def test_graph_execution(self):
        """Test the minimal graph execution functionality"""
        graph = ProdxyGraph([
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
        ])

        # Test graph structure
        graph_structure = graph.compiled_graph.get_graph()
        self.assertIsNotNone(graph_structure)

        # Test graph execution
        result = graph({
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
        self.assertGreater(len(result.prodxy_trace), 0)

    def test_graph_structure_visualization(self):
        """Test that the graph can be visualized (ASCII representation)"""
        graph = ProdxyGraph([
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
        ])

        # Test that ASCII representation can be generated
        # This is mainly to ensure the graph structure is valid
        try:
            graph.compiled_graph.get_graph().print_ascii()
        except Exception as e:
            self.fail(f"Graph ASCII visualization failed: {e}")


if __name__ == "__main__":
    unittest.main()