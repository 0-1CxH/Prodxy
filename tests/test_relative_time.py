import unittest
from prodxy.operation.relative_time import RelativeTimePrimitives

class TestRelativeTimePrimitives(unittest.TestCase):
    
    def setUp(self):
        self.rtp = RelativeTimePrimitives()

    def test_calculate_date(self):
        """Test calculate_date method"""
        
        # Basic test cases
        test_cases = [
            # (reference_date, shift, expected_result, description)
            ("2024-01-07", "-8D", "2023-12-30", "8 days ago"),
            ("2024-01-07", "-5D", "2024-01-02", "5 days ago"),
            ("2024-01-07", "0D", "2024-01-07", "Same day"),
            ("2024-01-07", "+1D", "2024-01-08", "1 day later"),
            ("2024-01-07", "10D", "2024-01-17", "10 days later"),

            # Month shift tests
            ("2024-01-07", "-2m3", "2023-11-03", "3rd day of 11th month"),
            ("2024-01-07", "-1m-4", "2023-12-28", "4th to last day of 12th month"),
            ("2024-01-07", "0m+10", "2024-01-10", "10th day of 1st month"),
            ("2024-01-07", "2m5", "2024-03-05", "5th day of 3rd month"),
            ("2024-01-07", "+3m-1", "2024-04-30", "Last day of 4th month"),

            # Week shift tests
            ("2024-01-07", "-2w3", "2023-12-20", "Wednesday 2 weeks ago (2024-01-07 is Sunday, 2 weeks ago is 2023-12-24, Wednesday is 2023-12-20)"),
            ("2024-01-07", "-1w4", "2023-12-28", "Thursday 1 week ago"),
            ("2024-01-07", "0w6", "2024-01-06", "Saturday of this week"),
            ("2024-01-07", "2w5", "2024-01-19", "Friday 2 weeks later"),
            ("2024-01-07", "+3w7", "2024-01-28", "Sunday 3 weeks later"),

            # Last/Next week tests
            ("2024-01-07", "Lastw3", "2024-01-03", "Last Wednesday (2024-01-07 is Sunday, this Wednesday is 2024-01-03)"),
            ("2024-01-07", "Nextw5", "2024-01-12", "Next Friday (2024-01-07 is Sunday, next Friday is 2024-01-12)"),

            # Boundary tests
            ("2024-12-31", "+1D", "2025-01-01", "New Year"),
            ("2024-02-28", "+1D", "2024-02-29", "Leap year February"),
        ]

        for ref_date, shift, expected, desc in test_cases:
            with self.subTest(desc=desc, ref_date=ref_date, shift=shift):
                result = self.rtp.calculate_date(ref_date, shift)
                self.assertEqual(result, expected, f"{desc}: {ref_date} {shift} => {result}, expected {expected}")

    def test_calculate_time(self):
        """Test calculate_time method"""
        
        test_cases = [
            # (reference_time, shift, expected_result, description)
            ("2024-01-07 10:30:00", "-8H30M", "2024-01-07 02:00:00", "8 hours 30 minutes ago"),
            ("2024-01-07 10:30:00", "-2H30S", "2024-01-07 08:29:30", "2 hours 30 seconds ago"),
            ("2024-01-07 10:30:00", "1H", "2024-01-07 11:30:00", "1 hour later"),
            ("2024-01-07 10:30:00", "+1M20S", "2024-01-07 10:31:20", "1 minute 20 seconds later"),
            ("2024-01-07 10:30:00", "20H30M15S", "2024-01-08 07:00:15", "20 hours 30 minutes 15 seconds later"),

            # 12-hour format nearest time tests
            ("2024-01-07 10:30:00", "C12Last8", "2024-01-07 08:00:00", "Last 8 AM"),
            ("2024-01-07 07:30:00", "C12Last8:00", "2024-01-06 20:00:00", "Last 8 PM (previous day)"),
            ("2024-01-07 08:00:00", "C12Next10:30", "2024-01-07 10:30:00", "Next 10:30"),
            ("2024-01-07 11:30:00", "C12Next10:30", "2024-01-07 22:30:00", "Next 10:30 PM"),

            # 24-hour format nearest time tests (C24 optional)
            ("2024-01-07 10:30:00", "C24Last8", "2024-01-07 08:00:00", "Last 8:00"),
            ("2024-01-07 07:30:00", "C24Last8:00", "2024-01-06 08:00:00", "Last 8:00 (previous day)"),
            ("2024-01-07 08:00:00", "Next10:30", "2024-01-07 10:30:00", "Next 10:30"),
            ("2024-01-07 11:30:00", "Next10:30", "2024-01-08 10:30:00", "Next 10:30 (next day)"),
        ]

        for ref_time, shift, expected, desc in test_cases:
            with self.subTest(desc=desc, ref_time=ref_time, shift=shift):
                result = self.rtp.calculate_time(ref_time, shift)
                self.assertEqual(result, expected, f"{desc}: {ref_time} {shift} => {result}, expected {expected}")

    def test_calculate_datetime(self):
        """Test calculate_datetime method"""
        
        test_cases = [
            # (reference_datetime, shift, expected_result, description)
            ("2024-01-07 10:30:00", "0w1 9:00", "2024-01-01 09:00:00", "Monday of this week 9:00"),
            ("2024-01-07 10:30:00", "1m5 10:30:19", "2024-02-05 10:30:19", "Feb 5th 10:30:19"),
            ("2024-01-07 10:30:00", "1D Next8", "2024-01-09 08:00:00", "Next 8:00 after 1 day"),
            ("2024-01-07 07:30:00", "1D Next8", "2024-01-08 08:00:00", "Next 8:00 after 1 day"),
        ]

        for ref_dt, shift, expected, desc in test_cases:
            with self.subTest(desc=desc, ref_dt=ref_dt, shift=shift):
                result = self.rtp.calculate_datetime(ref_dt, shift)
                self.assertEqual(result, expected, f"{desc}: {ref_dt} {shift} => {result}, expected {expected}")

    def test_compare_datetime(self):
        """Test compare_datetime method"""
        
        test_cases = [
            # (target, source, expected_seconds, description)
            ("2024-01-07", "2024-01-01", 6*24*3600, "Date diff 6 days"),
            ("2024-01-07", "2024-01-07 10:30:00", 0, "Same day, ignore time"),
            ("2024-01-07", "2024-01-08 10:30:00", 24*3600, "Date diff 1 day, ignore time"),

            ("10:30:00", "08:00:00", 2.5*3600, "Time diff 2.5 hours"),
            ("10:30", "08:00:00", 2.5*3600, "Time diff 2.5 hours (default seconds 00)"),
            ("10:30:00", "2024-01-07 08:00:00", 2.5*3600, "Time diff 2.5 hours (ignore date)"),

            ("2024-01-07 10:30:00", "2024-01-07 08:00:00", 2.5*3600, "Datetime diff 2.5 hours"),
            ("2024-01-07 10:30", "2024-01-07 08:00:00", 2.5*3600, "Datetime diff 2.5 hours (default seconds 00)"),
            ("2024-01-07 10:30:00", "2024-01-08 08:00:00", 21.5*3600, "Datetime diff 21.5 hours"),
        ]

        for target, source, expected_seconds, desc in test_cases:
            with self.subTest(desc=desc, target=target, source=source):
                result = self.rtp.compare_datetime(target, source)
                self.assertLess(abs(result - expected_seconds), 0.1, f"{desc}: {target} vs {source} => {result}s, expected {expected_seconds}s")

if __name__ == "__main__":
    unittest.main()