import unittest
from collections import Counter
from datetime import datetime

from prodxy.operation.value_generator import ValueGeneratorPrimitives

class TestValueGeneratorPrimitives(unittest.TestCase):
    def test_enum(self):
        # Test list with replacement
        items = ['a', 'b', 'c']
        res = ValueGeneratorPrimitives.enum(items, count=10, allow_repeat=True)
        self.assertEqual(len(res), 10)
        self.assertTrue(all(x in items for x in res))
        
        # Test list without replacement
        res = ValueGeneratorPrimitives.enum(items, count=3, allow_repeat=False)
        self.assertEqual(len(res), 3)
        self.assertEqual(set(res), set(items))
        
        # Test weights
        weights = {'a': 100, 'b': 1}
        res = ValueGeneratorPrimitives.enum(weights, count=100, allow_repeat=True)
        counts = Counter(res)
        self.assertGreater(counts['a'], counts['b'])
        
        # Test weighted without replacement
        a_count = 0
        for _ in range(100):
            res = ValueGeneratorPrimitives.enum(weights, count=1, allow_repeat=False)
            if res[0] == 'a':
                a_count += 1
        self.assertGreater(a_count, 80)

    def test_range(self):
        # Int range
        res = ValueGeneratorPrimitives.range((1, 10), is_integer=True, count=5)
        self.assertEqual(len(res), 5)
        self.assertTrue(all(isinstance(x, int) for x in res))
        self.assertTrue(all(1 <= x <= 10 for x in res))
        
        # Float range
        res = ValueGeneratorPrimitives.range(1.0, is_integer=False, count=5)
        self.assertEqual(len(res), 5)
        self.assertTrue(all(isinstance(x, float) for x in res))
        self.assertTrue(all(0.0 <= x <= 1.0 for x in res))

    def test_date(self):
        # Single boundary
        res = ValueGeneratorPrimitives.date("2025-01-01", is_sequential=True, count=5)
        self.assertEqual(len(res), 5)
        # Check format
        for d in res:
            datetime.strptime(d, "%Y-%m-%d")
        # Check sequential
        sorted_res = sorted(res)
        self.assertEqual(res, sorted_res)
        
        # Range
        res = ValueGeneratorPrimitives.date(("2020-01-01", "2020-01-05"), is_sequential=False, count=10)
        self.assertTrue(all("2020-01-01" <= x <= "2020-01-05" for x in res))

    def test_time(self):
        # Single boundary
        res = ValueGeneratorPrimitives.time("12:00:00", is_sequential=True, count=5)
        self.assertEqual(len(res), 5)
        # Check format
        for t in res:
            datetime.strptime(t, "%H:%M:%S")
        # Check sequential
        sorted_res = sorted(res)
        self.assertEqual(res, sorted_res)
        
        # Range
        res = ValueGeneratorPrimitives.time(("10:00:00", "11:00:00"), is_sequential=False, count=5)
        self.assertTrue(all("10:00:00" <= x <= "11:00:00" for x in res))

if __name__ == '__main__':
    unittest.main()
