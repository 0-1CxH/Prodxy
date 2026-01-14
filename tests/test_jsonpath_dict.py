import unittest
import json
import os
import tempfile
from prodxy.graph.analyzer import JsonPathAnalyzer, JsonPathDict

class TestJsonPathAnalyzer(unittest.TestCase):
    def setUp(self):
        self.data = {
            "store": {
                "book": [
                    {"category": "reference", "author": "Nigel Rees", "title": "Sayings of the Century", "price": 8.95},
                    {"category": "fiction", "author": "Evelyn Waugh", "title": "Sword of Honour", "price": 12.99}
                ],
                "bicycle": {
                    "color": "red",
                    "price": 19.95
                }
            }
        }

    def test_get(self):
        # Test simple get
        self.assertEqual(JsonPathAnalyzer.get(self.data, "$.store.bicycle.color"), "red")
        # Test list get
        books = JsonPathAnalyzer.get(self.data, "$.store.book[*].author")
        self.assertEqual(books, ["Nigel Rees", "Evelyn Waugh"])
        # Test not found
        self.assertIsNone(JsonPathAnalyzer.get(self.data, "$.store.car"))

    def test_set_simple(self):
        JsonPathAnalyzer.set(self.data, "$.store.bicycle.color", "blue")
        self.assertEqual(self.data["store"]["bicycle"]["color"], "blue")

    def test_set_list_index(self):
        # Set specific index in list
        JsonPathAnalyzer.set(self.data, "$.store.book[*].price", 10.00, on_index=0)
        self.assertEqual(self.data["store"]["book"][0]["price"], 10.00)
        self.assertEqual(self.data["store"]["book"][1]["price"], 12.99)
        
        # Set multiple indices
        JsonPathAnalyzer.set(self.data, "$.store.book[*].price", 20.00, on_index=[0, 1])
        self.assertEqual(self.data["store"]["book"][0]["price"], 20.00)
        self.assertEqual(self.data["store"]["book"][1]["price"], 20.00)

class TestJsonPathDict(unittest.TestCase):
    def setUp(self):
        self.raw_data = {"a": 1, "b": {"c": 2}, "d": [1, 2, 3]}
        self.jp_dict = JsonPathDict(self.raw_data)

    def test_getitem(self):
        self.assertEqual(self.jp_dict["$.a"], 1)
        self.assertEqual(self.jp_dict["$.b.c"], 2)
        self.assertEqual(self.jp_dict["$.d[0]"], 1)

    def test_setitem(self):
        self.jp_dict["$.a"] = 10
        self.assertEqual(self.raw_data["a"], 10)
        
        self.jp_dict["$.b.c"] = 20
        self.assertEqual(self.raw_data["b"]["c"], 20)
        
        # Test tuple key for index
        self.jp_dict["$.d[*]", 1] = 99
        self.assertEqual(self.raw_data["d"][1], 99)
        self.assertEqual(self.raw_data["d"][0], 1)

    def test_delitem(self):
        del self.jp_dict["$.a"]
        self.assertIsNone(self.raw_data["a"]) # Implementation sets to None

    def test_contains(self):
        self.assertTrue("$.a" in self.jp_dict)
        self.assertFalse("$.z" in self.jp_dict)

    def test_load_dump_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.raw_data, f)
            fname = f.name
        
        try:
            # Load
            loaded = JsonPathDict.load(fname)
            self.assertEqual(loaded["$.a"], 1)
            
            # Modify and Dump
            loaded["$.a"] = 2
            loaded.dump()
            
            # Verify dump
            with open(fname, 'r') as f:
                new_data = json.load(f)
            self.assertEqual(new_data["a"], 2)
        finally:
            os.remove(fname)

    def test_load_dump_jsonl(self):
        data = [{"id": 1}, {"id": 2}]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for item in data:
                f.write(json.dumps(item) + '\n')
            fname = f.name

        try:
            # Load
            loaded = JsonPathDict.load(fname)
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded["$[0].id"], 1)

            # Modify and Dump
            loaded["$[0].id"] = 3
            loaded.dump()

            # Verify dump
            with open(fname, 'r') as f:
                lines = [json.loads(line) for line in f]
            self.assertEqual(lines[0]["id"], 3)
        finally:
            os.remove(fname)

    def test_basic_functionality_setting_new_value(self):
        """Test 1: Basic functionality - setting a value when the path doesn't exist"""
        d = {}
        json_dict = JsonPathDict(d)
        json_dict['user.name'] = "John"
        self.assertEqual(d, {"user": {"name": "John"}})
        self.assertEqual(json_dict['user.name'], "John")

    def test_setting_nested_values(self):
        """Test 2: Setting nested values"""
        d = {}
        json_dict = JsonPathDict(d)
        json_dict['user.profile.age'] = 30
        json_dict['user.profile.email'] = "john@example.com"
        expected = {"user": {"profile": {"age": 30, "email": "john@example.com"}}}
        self.assertEqual(d, expected)
        self.assertEqual(json_dict['user.profile.age'], 30)
        self.assertEqual(json_dict['user.profile.email'], "john@example.com")

    def test_array_access(self):
        """Test 3: Array access"""
        d = {}
        json_dict = JsonPathDict(d)
        json_dict['users[0].name'] = "Alice"
        json_dict['users[1].name'] = "Bob"
        expected = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        self.assertEqual(d, expected)
        self.assertEqual(json_dict['users[0].name'], "Alice")
        self.assertEqual(json_dict['users[1].name'], "Bob")

    def test_mixed_nested_objects_and_arrays(self):
        """Test 4: Mixed nested objects and arrays"""
        d = {}
        json_dict = JsonPathDict(d)
        json_dict['company.departments[0].name'] = "Engineering"
        json_dict['company.departments[0].employees[0].name'] = "Charlie"
        expected = {
            "company": {
                "departments": [
                    {
                        "name": "Engineering",
                        "employees": [{"name": "Charlie"}]
                    }
                ]
            }
        }
        self.assertEqual(d, expected)
        self.assertEqual(json_dict['company.departments[0].name'], "Engineering")
        self.assertEqual(json_dict['company.departments[0].employees[0].name'], "Charlie")

    def test_updating_existing_values(self):
        """Test 5: Updating existing values"""
        d = {'user': {'name': 'John'}}
        json_dict = JsonPathDict(d)
        json_dict['user.name'] = "John Doe"
        expected = {'user': {'name': 'John Doe'}}
        self.assertEqual(d, expected)
        self.assertEqual(json_dict['user.name'], "John Doe")

if __name__ == '__main__':
    unittest.main()
