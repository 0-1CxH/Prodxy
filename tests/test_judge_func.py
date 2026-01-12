from prodxy.operation.judge_func import JudgePrimitives

def test_equal():
    """Test the equal method"""
    print("Testing equal method...")

    # Test 1: Non-container types
    assert JudgePrimitives.equal(42, 42) == True, "Equal numbers should return True"
    assert JudgePrimitives.equal(42, 43) == False, "Different numbers should return False"
    assert JudgePrimitives.equal("hello", "hello") == True, "Equal strings should return True"
    assert JudgePrimitives.equal("hello", "world") == False, "Different strings should return False"

    # Test 2: Non-kv container types (lists)
    assert JudgePrimitives.equal([1, 2, 3], [1, 2, 3]) == True, "Equal lists should return True"
    assert JudgePrimitives.equal([1, 2, 3], [1, 3, 2]) == False, "Lists with different order should return False"
    assert JudgePrimitives.equal([1, 2, 3], [1, 2]) == False, "Lists with different lengths should return False"

    # Test 3: Non-kv container types (tuples)
    assert JudgePrimitives.equal((1, 2, 3), (1, 2, 3)) == True, "Equal tuples should return True"
    assert JudgePrimitives.equal((1, 2, 3), (1, 3, 2)) == False, "Tuples with different order should also return True (only compare elems)"

    # Test 4: Non-kv container types (sets)
    assert JudgePrimitives.equal({1, 2, 3}, {1, 2, 3}) == True, "Equal sets should return True"
    assert JudgePrimitives.equal({1, 2, 3}, {3, 2, 1}) == True, "Sets with same elements in different order should return True"
    assert JudgePrimitives.equal({1, 2, 3}, {1, 2}) == False, "Sets with different elements should return False"

    # Test 5: Mixed set and list
    assert JudgePrimitives.equal([1, 2, 3], {1, 2, 3}) == True, "List and set should return True with same elements"
    assert JudgePrimitives.equal({1, 2, 3}, [1, 2, 3]) == True, "Set and list should return True with same elements"
    assert JudgePrimitives.equal({1, 2, 3}, (1, 2, 3)) == True, "Set and tuple should return True with same elements"
    assert JudgePrimitives.equal([1, 2, 3], (1, 2, 3)) == True, "List and tuple should return True with same elements"

    # Test 6: Kv-container types (dicts)
    assert JudgePrimitives.equal({"a": 1, "b": 2}, {"a": 1, "b": 2}) == True, "Equal dicts should return True"
    assert JudgePrimitives.equal({"a": 1, "b": 2}, {"b": 2, "a": 1}) == True, "Dicts with same items in different order should return True"
    assert JudgePrimitives.equal({"a": 1, "b": 2}, {"a": 1, "c": 2}) == False, "Dicts with different keys should return False"
    assert JudgePrimitives.equal({"a": 1, "b": 2}, {"a": 1, "b": 3}) == False, "Dicts with different values should return False"

    # Test 7: Nested structures
    assert JudgePrimitives.equal([1, {"a": 2}, 3], [1, {"a": 2}, 3]) == True, "Equal nested structures should return True"
    assert JudgePrimitives.equal([1, {"a": 2}, 3], [1, {"a": 3}, 3]) == False, "Different nested structures should return False"
    assert JudgePrimitives.equal({"list": [1, 2, 3]}, {"list": [1, 2, 3]}) == True, "Dict with list should return True"
    assert JudgePrimitives.equal({"list": [1, 2, 3]}, {"list": [1, 3, 2]}) == True, "The inside list is 'equal' with JudgePrimitives"

    # Test 8: Type mismatch
    assert JudgePrimitives.equal(42, "42") == True, "42 could be converted to string ans True"
    assert JudgePrimitives.equal([1, 2], (1, 2)) == True, "List vs tuple but same elems"
    assert JudgePrimitives.equal({"a": 1}, [("a", 1)]) == False, "Not same"

    print("All equal tests passed!")

def test_include():
    """Test the include method"""
    print("\nTesting include method...")

    # Test 1: String target
    assert JudgePrimitives.include("hello world", "hello") == True, "String should include substring"
    assert JudgePrimitives.include("hello world", "world") == True, "String should include substring"
    assert JudgePrimitives.include("hello world", "goodbye") == False, "String should not include non-substring"
    assert JudgePrimitives.include("123", 123) == True, "String should include number converted to string"
    assert JudgePrimitives.include("123456", 45) == True, "String should include number converted to string"


    # Test 2: List target with non-container source
    assert JudgePrimitives.include([1, 2, 3], 2) == True, "List should include element"
    assert JudgePrimitives.include([1, 2, 3], 4) == False, "List should not include non-element"
    assert JudgePrimitives.include(["a", "b", "c"], "b") == True, "List should include string element"

    # Test 3: List target with list source
    assert JudgePrimitives.include([1, 2, 3, 4], [2, 3]) == True, "List should include sublist"
    assert JudgePrimitives.include([1, 2, 3, 4], [3, 5]) == False, "List should not include sublist with missing element"
    assert JudgePrimitives.include([1, 2, 3, 4], [4, 1]) == True, "List should include sublist regardless of order"
    assert JudgePrimitives.include([1, 2, 3, 4], (2, 1)) == True, "List should include sublist regardless of order"
    

    # Test 4: Set target
    assert JudgePrimitives.include({1, 2, 3}, 2) == True, "Set should include element"
    assert JudgePrimitives.include({1, 2, 3}, {2, 3}) == True, "Set should include subset"
    assert JudgePrimitives.include({1, 2, 3}, {2, 4}) == False, "Set should not include subset with missing element"
    assert JudgePrimitives.include({1, 2, 3}, [2, 1]) == True, "Set should include subset even in list"

    # Test 5: Dict target with non-container source
    assert JudgePrimitives.include({"a": 1, "b": 2}, "a") == True, "Dict should include key"
    assert JudgePrimitives.include({"a": 1, "b": 2}, ["a", "b"]) == True, "Dict should include keys"
    assert JudgePrimitives.include({"a": 1, "b": 2}, 1) == True, "Dict should include value"
    assert JudgePrimitives.include({"a": 1, "b": 2}, [1,2]) == True, "Dict should include values"
    assert JudgePrimitives.include({"a": 1, "b": 2}, [1,"b"]) == False, "Dict should not include mix of keys and values"
    assert JudgePrimitives.include({"a": 1, "b": 2}, "c") == False, "Dict should not include non-key"
    assert JudgePrimitives.include({"a": 1, "b": 2}, 3) == False, "Dict should not include non-value"

    # Test 6: Dict target with dict source
    assert JudgePrimitives.include({"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 2}) == True, "Dict should include sub-dict"
    assert JudgePrimitives.include({"a": 1, "b": 2, "c": 3}, {"a": 1, "d": 4}) == False, "Dict should not include sub-dict with missing key"
    assert JudgePrimitives.include({"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 3}) == False, "Dict should not include sub-dict with wrong value"

    # Test 7: Recursive include
    assert JudgePrimitives.include([{"a": 1}, {"b": 2}], {"a": 1}, recursive=True) == True, "Recursive include should find dict in list"
    assert JudgePrimitives.include([{"a": 1}, {"b": 2}], {"a": 1}, recursive=False) == False, "Non-recursive include should not find dict in list"
    assert JudgePrimitives.include({"x": [1, 2, 3]}, 2, recursive=True) == True, "Recursive include should find value in nested list"
    assert JudgePrimitives.include({"x": [1, 2, 3]}, 2, recursive=False) == False, "Non-recursive include should not find value in nested list"

    # Test 8: Tuple target
    assert JudgePrimitives.include((1, 2, 3), 2) == True, "Tuple should include element"
    assert JudgePrimitives.include((1, 2, 3), (2, 3)) == True, "Tuple should include subtuple"

    print("All include tests passed!")

def test_edge_cases():
    """Test edge cases"""
    print("\nTesting edge cases...")

    # Empty containers
    assert JudgePrimitives.equal([], []) == True, "Empty lists should be equal"
    assert JudgePrimitives.equal({}, {}) == True, "Empty dicts should be equal"
    assert JudgePrimitives.include([], 1) == False, "Empty list should not include anything"
    assert JudgePrimitives.include({}, "key") == False, "Empty dict should not include anything"

    # Nested empty containers
    assert JudgePrimitives.equal({"a": []}, {"a": []}) == True, "Dicts with empty lists should be equal"
    assert JudgePrimitives.include({"a": []}, [], recursive=True) == True, "Recursive include should find empty list"

    # None values
    assert JudgePrimitives.equal(None, None) == True, "None should equal None"
    assert JudgePrimitives.equal(None, 0) == False, "None should not equal 0"
    assert JudgePrimitives.include([None, 1, 2], None) == True, "List should include None"

    # Boolean values
    assert JudgePrimitives.equal(True, True) == True, "True should equal True"
    assert JudgePrimitives.equal(False, False) == True, "False should equal False"
    assert JudgePrimitives.equal(True, False) == False, "True should not equal False"
    assert JudgePrimitives.include([True, False], True) == True, "List should include True"

    # Float values
    assert JudgePrimitives.equal(3.14, 3.14) == True, "Floats should be equal"
    assert JudgePrimitives.equal(3.14, 3.140) == True, "Floats with different precision should be equal"

    print("All edge case tests passed!")

def main():
    """Run all tests"""
    try:
        test_equal()
        test_include()
        test_edge_cases()
        print("\n✅ All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    main()