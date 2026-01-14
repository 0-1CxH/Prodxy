import unittest
from prodxy.graph.analyzer import FieldCentricAnalyzer

class TestFieldCentricAnalyzer(unittest.TestCase):
    
    def assert_dict_lists_match(self, result_list, expected_list):
        """Check that each dict in result_list contains at least the key-value pairs in corresponding expected dict."""
        self.assertEqual(len(result_list), len(expected_list), f"Length mismatch: {len(result_list)} != {len(expected_list)}")
        for res, exp in zip(result_list, expected_list):
            for k, v in exp.items():
                self.assertIn(k, res, f"Missing key {k} in result dict {res}")
                self.assertEqual(res[k], v, f"Value mismatch for key {k}: {res[k]} != {v}")

    def test_examples_from_docstring(self):
        """Test all examples provided in the class docstring."""
        data = FieldCentricAnalyzer([
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 3, "c": 4, "d": 1},
            {"a": 2, "b": 3, "c": 4},
            {"a": 2, "b": 4, "c": 5, "d": 2},
        ])

        # data.a(1) -> FieldCentricAnalyzer([{"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 3, "c": 4}])
        res = data.a(1)
        expected = [{"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 3, "c": 4}]
        self.assert_dict_lists_match(res._data, expected)

        # data.a(1)[0] -> FieldCentricAnalyzer([{"a": 1, "b": 2, "c": 3}])
        res = data.a(1)[0]
        expected = [{"a": 1, "b": 2, "c": 3}]
        self.assert_dict_lists_match(res._data, expected)

        # data.b(3) = data.b(3, "eq") -> FieldCentricAnalyzer([{"a": 1, "b": 3, "c": 4}, {"a": 2, "b": 3, "c": 4}])
        res = data.b(3)
        expected = [{"a": 1, "b": 3, "c": 4}, {"a": 2, "b": 3, "c": 4}]
        self.assert_dict_lists_match(res._data, expected)

        # data.b(3, "gt") -> FieldCentricAnalyzer([{"a": 2, "b": 4, "c": 5}])
        res = data.b(3, "gt")
        expected = [{"a": 2, "b": 4, "c": 5}]
        self.assert_dict_lists_match(res._data, expected)

        # data.d("*") -> FieldCentricAnalyzer([{"a": 1, "b": 3, "c": 4, "d": 1}, {"a": 2, "b": 4, "c": 5, "d": 2}])
        res = data.d("*")
        expected = [{"a": 1, "b": 3, "c": 4, "d": 1}, {"a": 2, "b": 4, "c": 5, "d": 2}]
        self.assertEqual(res._data, expected, f"Expected {expected}, got {res._data}")

        # data.a(3) -> FieldCentricAnalyzer([])
        res = data.a(3)
        self.assertEqual(res._data, [])

        # data.a(3)[2] -> None
        res = data.a(3)[2]
        self.assertIsNone(res)

        # data.a -> FieldCentricAnalyzer([1, 1, 2, 2])
        res = data.a
        self.assertEqual(res._mode, "values")
        self.assertEqual(res._data, [1, 1, 2, 2])

        # data.a[2] -> 2
        res = data.a[2]
        self.assertEqual(res, 2)

        # data.d -> FieldCentricAnalyzer([1, 2])
        res = data.d
        self.assertEqual(res._mode, "values")
        self.assertEqual(res._data, [1, 2])

        # data.d[2] -> None
        res = data.d[2]
        self.assertIsNone(res)

    def test_operators(self):
        """Test all comparison operators."""
        data = FieldCentricAnalyzer([
            {"x": 5},
            {"x": 10},
            {"x": 15},
            {"y": 20},
        ])

        # eq
        res = data.x(10)
        self.assertTrue(len(res._data) == 1 and res._data[0]["x"] == 10)
        # gt
        res = data.x(10, "gt")
        self.assertTrue(len(res._data) == 1 and res._data[0]["x"] == 15)
        # lt
        res = data.x(10, "lt")
        self.assertTrue(len(res._data) == 1 and res._data[0]["x"] == 5)
        # ge
        res = data.x(10, "ge")
        self.assertEqual(len(res._data), 2)
        # le
        res = data.x(10, "le")
        self.assertEqual(len(res._data), 2)

    def test_missing_field(self):
        """Test behavior when field is missing in all dicts."""
        data = FieldCentricAnalyzer([{"a": 1}, {"b": 2}])
        res = data.c
        self.assertEqual(res._mode, "values")
        self.assertEqual(res._data, [])
        # calling with "*" returns empty
        res2 = data.c("*")
        self.assertEqual(res2._data, [])
        # calling with value returns empty
        res3 = data.c(5)
        self.assertEqual(res3._data, [])

    def test_empty_data(self):
        """Test with empty list."""
        data = FieldCentricAnalyzer([])
        res = data.some_field
        self.assertEqual(res._mode, "values")
        self.assertEqual(res._data, [])
        res2 = data.some_field("*")
        self.assertEqual(res2._data, [])

    def test_chaining(self):
        """Test chaining of filters."""
        data = FieldCentricAnalyzer([
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 2, "c": 4},
            {"a": 2, "b": 2, "c": 5},
        ])
        res = data.a(1).b(2)
        self.assertEqual(len(res._data), 2)
        self.assertTrue(all(d["a"] == 1 and d["b"] == 2 for d in res._data))
        # further indexing
        res2 = data.a(1).b(2)[0]
        self.assertEqual(len(res2._data), 1)
        # attribute access on result
        res3 = data.a(1).b(2)[0].c
        self.assertEqual(res3._data, [3])

    def test_repr(self):
        """Test string representation."""
        data = FieldCentricAnalyzer([{"x": 1}])
        self.assertEqual(repr(data), "FieldCentricAnalyzer([{'x': 1}])")
        val = data.x
        self.assertEqual(repr(val), "FieldCentricAnalyzer([1])")

    def test_iteration_grouping(self):
        """Test iteration over value-mode analyzer for grouping."""
        data = FieldCentricAnalyzer([
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 3, "c": 4, "d": 1},
            {"a": 2, "b": 3, "c": 4},
            {"a": 2, "b": 4, "c": 5, "d": 2},
        ])

        results = []
        for group_name, group_values in data.a:
            results.append((group_name, group_values._data))

        # Should have 2 groups: a=1 and a=2
        self.assertEqual(len(results), 2)

        # Check group a=1
        self.assertEqual(results[0][0], 1)
        self.assertEqual(len(results[0][1]), 2)
        # Check dicts in group a=1 (order may vary)
        group1_dicts = results[0][1]
        # Should contain both dicts with a=1
        has_first = any(d.get("b") == 2 and d.get("c") == 3 for d in group1_dicts)
        has_second = any(d.get("b") == 3 and d.get("c") == 4 for d in group1_dicts)
        self.assertTrue(has_first and has_second)

        # Check group a=2
        self.assertEqual(results[1][0], 2)
        self.assertEqual(len(results[1][1]), 2)

    def test_iteration_filtered(self):
        """Test iteration over dict-mode analyzer (filtered results)."""
        data = FieldCentricAnalyzer([
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 3, "c": 4, "d": 1},
            {"a": 2, "b": 3, "c": 4},
            {"a": 2, "b": 4, "c": 5, "d": 2},
        ])

        results = []
        for value in data.a(1):
            results.append(value)

        # Should have 2 dicts where a=1
        self.assertEqual(len(results), 2)
        # Check they both have a=1
        self.assertTrue(all(d["a"] == 1 for d in results))
        # Check specific values
        has_first = any(d.get("b") == 2 and d.get("c") == 3 for d in results)
        has_second = any(d.get("b") == 3 and d.get("c") == 4 for d in results)
        self.assertTrue(has_first and has_second)

    def test_iteration_dict_mode(self):
        """Test iteration over raw dict-mode analyzer."""
        data = FieldCentricAnalyzer([
            {"x": 1},
            {"x": 2},
        ])

        results = list(data)  # data is in dicts mode
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], {"x": 1})
        self.assertEqual(results[1], {"x": 2})

if __name__ == "__main__":
    unittest.main()