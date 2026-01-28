import unittest
from prodxy.operation.judge_func import JudgePrimitives

class TestJudgePrimitives(unittest.TestCase):
    
    def test_equal(self):
        """Test the equal method"""
        
        # Test 1: Non-container types
        self.assertTrue(JudgePrimitives.equal(42, 42), "Equal numbers should return True")
        self.assertFalse(JudgePrimitives.equal(42, 43), "Different numbers should return False")
        self.assertTrue(JudgePrimitives.equal("hello", "hello"), "Equal strings should return True")
        self.assertFalse(JudgePrimitives.equal("hello", "world"), "Different strings should return False")

        # Test 2: Non-kv container types (lists)
        self.assertTrue(JudgePrimitives.equal([1, 2, 3], [1, 2, 3]), "Equal lists should return True")
        self.assertFalse(JudgePrimitives.equal([1, 2, 3], [1, 3, 2]), "Lists with different order should return False")
        self.assertFalse(JudgePrimitives.equal([1, 2, 3], [1, 2]), "Lists with different lengths should return False")

        # Test 3: Non-kv container types (tuples)
        self.assertTrue(JudgePrimitives.equal((1, 2, 3), (1, 2, 3)), "Equal tuples should return True")
        self.assertFalse(JudgePrimitives.equal((1, 2, 3), (1, 3, 2)), "Tuples with different order should also return True (only compare elems)")

        # Test 4: Non-kv container types (sets)
        self.assertTrue(JudgePrimitives.equal({1, 2, 3}, {1, 2, 3}), "Equal sets should return True")
        self.assertTrue(JudgePrimitives.equal({1, 2, 3}, {3, 2, 1}), "Sets with same elements in different order should return True")
        self.assertFalse(JudgePrimitives.equal({1, 2, 3}, {1, 2}), "Sets with different elements should return False")

        # Test 5: Mixed set and list
        self.assertTrue(JudgePrimitives.equal([1, 2, 3], {1, 2, 3}), "List and set should return True with same elements")
        self.assertTrue(JudgePrimitives.equal({1, 2, 3}, [1, 2, 3]), "Set and list should return True with same elements")
        self.assertTrue(JudgePrimitives.equal({1, 2, 3}, (1, 2, 3)), "Set and tuple should return True with same elements")
        self.assertTrue(JudgePrimitives.equal([1, 2, 3], (1, 2, 3)), "List and tuple should return True with same elements")

        # Test 6: Kv-container types (dicts)
        self.assertTrue(JudgePrimitives.equal({"a": 1, "b": 2}, {"a": 1, "b": 2}), "Equal dicts should return True")
        self.assertTrue(JudgePrimitives.equal({"a": 1, "b": 2}, {"b": 2, "a": 1}), "Dicts with same items in different order should return True")
        self.assertFalse(JudgePrimitives.equal({"a": 1, "b": 2}, {"a": 1, "c": 2}), "Dicts with different keys should return False")
        self.assertFalse(JudgePrimitives.equal({"a": 1, "b": 2}, {"a": 1, "b": 3}), "Dicts with different values should return False")

        # Test 7: Nested structures
        self.assertTrue(JudgePrimitives.equal([1, {"a": 2}, 3], [1, {"a": 2}, 3]), "Equal nested structures should return True")
        self.assertFalse(JudgePrimitives.equal([1, {"a": 2}, 3], [1, {"a": 3}, 3]), "Different nested structures should return False")
        self.assertTrue(JudgePrimitives.equal({"list": [1, 2, 3]}, {"list": [1, 2, 3]}), "Dict with list should return True")
        self.assertTrue(JudgePrimitives.equal({"list": [1, 2, 3]}, {"list": [1, 3, 2]}), "The inside list is 'equal' with JudgePrimitives")

        # Test 8: Type mismatch
        self.assertTrue(JudgePrimitives.equal(42, "42"), "42 could be converted to string ans True")
        self.assertTrue(JudgePrimitives.equal([1, 2], (1, 2)), "List vs tuple but same elems")
        self.assertFalse(JudgePrimitives.equal({"a": 1}, [("a", 1)]), "Not same")

    def test_include(self):
        """Test the include method"""

        # Test 1: String target
        self.assertTrue(JudgePrimitives.include("hello world", "hello"), "String should include substring")
        self.assertTrue(JudgePrimitives.include("hello world", "world"), "String should include substring")
        self.assertFalse(JudgePrimitives.include("hello world", "goodbye"), "String should not include non-substring")
        self.assertTrue(JudgePrimitives.include("123", 123), "String should include number converted to string")
        self.assertTrue(JudgePrimitives.include("123456", 45), "String should include number converted to string")

        # Test 2: List target with non-container source
        self.assertTrue(JudgePrimitives.include([1, 2, 3], 2), "List should include element")
        self.assertFalse(JudgePrimitives.include([1, 2, 3], 4), "List should not include non-element")
        self.assertTrue(JudgePrimitives.include(["a", "b", "c"], "b"), "List should include string element")

        # Test 3: List target with list source
        self.assertTrue(JudgePrimitives.include([1, 2, 3, 4], [2, 3]), "List should include sublist")
        self.assertFalse(JudgePrimitives.include([1, 2, 3, 4], [3, 5]), "List should not include sublist with missing element")
        self.assertTrue(JudgePrimitives.include([1, 2, 3, 4], [4, 1]), "List should include sublist regardless of order")
        self.assertTrue(JudgePrimitives.include([1, 2, 3, 4], (2, 1)), "List should include sublist regardless of order")
        
        # Test 4: Set target
        self.assertTrue(JudgePrimitives.include({1, 2, 3}, 2), "Set should include element")
        self.assertTrue(JudgePrimitives.include({1, 2, 3}, {2, 3}), "Set should include subset")
        self.assertFalse(JudgePrimitives.include({1, 2, 3}, {2, 4}), "Set should not include subset with missing element")
        self.assertTrue(JudgePrimitives.include({1, 2, 3}, [2, 1]), "Set should include subset even in list")

        # Test 5: Dict target with non-container source
        self.assertTrue(JudgePrimitives.include({"a": 1, "b": 2}, "a"), "Dict should include key")
        self.assertTrue(JudgePrimitives.include({"a": 1, "b": 2}, ["a", "b"]), "Dict should include keys")
        self.assertTrue(JudgePrimitives.include({"a": 1, "b": 2}, 1), "Dict should include value")
        self.assertTrue(JudgePrimitives.include({"a": 1, "b": 2}, [1,2]), "Dict should include values")
        self.assertFalse(JudgePrimitives.include({"a": 1, "b": 2}, [1,"b"]), "Dict should not include mix of keys and values")
        self.assertFalse(JudgePrimitives.include({"a": 1, "b": 2}, "c"), "Dict should not include non-key")
        self.assertFalse(JudgePrimitives.include({"a": 1, "b": 2}, 3), "Dict should not include non-value")

        # Test 6: Dict target with dict source
        self.assertTrue(JudgePrimitives.include({"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 2}), "Dict should include sub-dict")
        self.assertFalse(JudgePrimitives.include({"a": 1, "b": 2, "c": 3}, {"a": 1, "d": 4}), "Dict should not include sub-dict with missing key")
        self.assertFalse(JudgePrimitives.include({"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 3}), "Dict should not include sub-dict with wrong value")

        # Test 7: Recursive include
        self.assertTrue(JudgePrimitives.include([{"a": 1}, {"b": 2}], {"a": 1}, recursive=True), "Recursive include should find dict in list")
        self.assertFalse(JudgePrimitives.include([{"a": 1}, {"b": 2}], {"a": 1}, recursive=False), "Non-recursive include should not find dict in list")
        self.assertTrue(JudgePrimitives.include({"x": [1, 2, 3]}, 2, recursive=True), "Recursive include should find value in nested list")
        self.assertFalse(JudgePrimitives.include({"x": [1, 2, 3]}, 2, recursive=False), "Non-recursive include should not find value in nested list")

        # Test 8: Tuple target
        self.assertTrue(JudgePrimitives.include((1, 2, 3), 2), "Tuple should include element")
        self.assertTrue(JudgePrimitives.include((1, 2, 3), (2, 3)), "Tuple should include subtuple")

    def test_edge_cases(self):
        """Test edge cases"""

        # Empty containers
        self.assertTrue(JudgePrimitives.equal([], []), "Empty lists should be equal")
        self.assertTrue(JudgePrimitives.equal({}, {}), "Empty dicts should be equal")
        self.assertFalse(JudgePrimitives.include([], 1), "Empty list should not include anything")
        self.assertFalse(JudgePrimitives.include({}, "key"), "Empty dict should not include anything")

        # Nested empty containers
        self.assertTrue(JudgePrimitives.equal({"a": []}, {"a": []}), "Dicts with empty lists should be equal")
        self.assertTrue(JudgePrimitives.include({"a": []}, [], recursive=True), "Recursive include should find empty list")

        # None values
        self.assertTrue(JudgePrimitives.equal(None, None), "None should equal None")
        self.assertFalse(JudgePrimitives.equal(None, 0), "None should not equal 0")
        self.assertTrue(JudgePrimitives.include([None, 1, 2], None), "List should include None")

        # Boolean values
        self.assertTrue(JudgePrimitives.equal(True, True), "True should equal True")
        self.assertTrue(JudgePrimitives.equal(False, False), "False should equal False")
        self.assertFalse(JudgePrimitives.equal(True, False), "True should not equal False")
        self.assertTrue(JudgePrimitives.include([True, False], True), "List should include True")

        # Float values
        self.assertTrue(JudgePrimitives.equal(3.14, 3.14), "Floats should be equal")
        self.assertTrue(JudgePrimitives.equal(3.14, 3.140), "Floats with different precision should be equal")

if __name__ == "__main__":
    unittest.main()