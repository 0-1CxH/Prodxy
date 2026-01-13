import re
from datetime import datetime, timedelta
from calendar import monthrange

class RelativeTimePrimitives:
    @staticmethod
    def calculate_date(reference_date, shift):
        """
        reference date should be in YYYY-mm-DD format, output is also in this format
        shift has multiple supported format:
            (1) [+/-x]D means x days before/after reference date
                x could be any integer, '+' could be omitted,
                e.g.    -8D (8 days before the reference date),
                        -5D (5 days before the reference date),
                        0D (the reference date),
                        +1D (1 day after the reference date),
                        10D (10 days after the reference date)
            (2) [+/-x]m[+/-y] means the y-th day from the start or end of the x months before/after reference date
                x could be any integer, y should be less than the number of days in the target month, both '+' could be omitted
                e.g.    -2m3 (the 3rd day that counted from the start of the 2nd month before the reference date's month),
                        -1m-4 (the 4th day that counted backwards from the end of the 1st month before reference date's month),
                        0m+10 (the 10th day that counted from the start of the reference date's month),
                        2m5 (the 5th day that counted from the start of the 2nd month after the reference date's month),
                        +3m-1 (the last day of the 3rd month after the reference date's month)
            (3) [+/-x]w[y] means the y-th day of the x weeks before/after reference date
                x could be any integer, y should be in range 1-7, '+' could be omitted
                e.g.    -2w3 (Wednesday of the 2nd week before the reference date's week),
                        -1w4 (Thursday of the 1st week before the reference date's week),
                        0w6 (Saturday of the reference date's week),
                        2w5 (Friday of the 2nd week after the reference date's week),
                        +3w7 (Sunday of the 3rd week after the reference date's week)
            (4) [Last/Next]w[y] means the nearest y-th day before/after the reference date's week
                y should be in range 1-7
                e.g.    Lastw3 (return the nearest previous Wednesday:
                                if reference date is Wednesday/Thursday/Friday/Saturday/Sunday, then return the Wednesday of this week,
                                if reference date is Monday/Tuesday, then return the Wednesday of last week),
                        Nextw5 (return the nearest next Friday:
                                if reference date is Friday/Saturday/Sunday, then return the Friday of this week,
                                if reference date is Monday/Tuesday/Wednesday/Thursday, then return the Friday of next week)
        """
        # Parse reference date
        ref_date = datetime.strptime(reference_date, "%Y-%m-%d")

        # Mode 1: [+/-x]D
        match = re.match(r'^([+-]?\d+)D$', shift)
        if match:
            days = int(match.group(1))
            result_date = ref_date + timedelta(days=days)
            return result_date.strftime("%Y-%m-%d")

        # Mode 2: [+/-x]m[+/-y]
        match = re.match(r'^([+-]?\d+)m([+-]?\d+)$', shift)
        if match:
            months = int(match.group(1))
            day_offset = int(match.group(2))

            # Calculate target year and month
            year = ref_date.year + (ref_date.month + months - 1) // 12
            month = (ref_date.month + months) % 12
            if month == 0:
                month = 12

            # Get number of days in that month
            _, days_in_month = monthrange(year, month)

            # Calculate target date
            if day_offset >= 0:
                # Count from the beginning of the month (1-based)
                target_day = day_offset
            else:
                # Count backwards from the end of the month
                # day_offset = -1 means the last day, -2 means the second to last day, etc.
                target_day = days_in_month + day_offset + 1

            # Ensure target date is within valid range
            if 1 <= target_day <= days_in_month:
                result_date = datetime(year, month, target_day)
                return result_date.strftime("%Y-%m-%d")
            else:
                raise ValueError(f"Day offset {day_offset} out of range for month {year}-{month:02d}")

        # Mode 3: [+/-x]w[y]
        match = re.match(r'^([+-]?\d+)w([1-7])$', shift)
        if match:
            weeks = int(match.group(1))
            weekday = int(match.group(2))  # 1=Monday, ..., 7=Sunday

            # Calculate Monday of the target week
            # ref_date's weekday: 0=Monday, ..., 6=Sunday
            ref_weekday = ref_date.weekday()  # 0-6 (Monday=0)
            days_to_monday = ref_weekday  # Days from this Monday
            monday_of_ref_week = ref_date - timedelta(days=days_to_monday)

            # Calculate Monday of the target week
            target_monday = monday_of_ref_week + timedelta(weeks=weeks)

            # Calculate target date (weekday: 1=Monday, ..., 7=Sunday)
            result_date = target_monday + timedelta(days=weekday-1)
            return result_date.strftime("%Y-%m-%d")

        # Mode 4: [Last/Next]w[y]
        match = re.match(r'^(Last|Next)w([1-7])$', shift, re.IGNORECASE)
        if match:
            direction = match.group(1).lower()
            weekday = int(match.group(2))  # 1=Monday, ..., 7=Sunday

            # ref_date's weekday: 0=Monday, ..., 6=Sunday
            ref_weekday = ref_date.weekday() + 1  # Convert to 1-7 (Monday=1)

            if direction == 'last':
                # Nearest previous weekday
                if ref_weekday >= weekday:
                    # Weekday of this week
                    days_diff = ref_weekday - weekday
                    result_date = ref_date - timedelta(days=days_diff)
                else:
                    # Weekday of last week
                    days_diff = weekday - ref_weekday
                    result_date = ref_date - timedelta(days=7 - days_diff)
            else:  # 'next'
                # Nearest next weekday
                if ref_weekday <= weekday:
                    # Weekday of this week
                    days_diff = weekday - ref_weekday
                    result_date = ref_date + timedelta(days=days_diff)
                else:
                    # Weekday of next week
                    days_diff = 7 - (ref_weekday - weekday)
                    result_date = ref_date + timedelta(days=days_diff)

            return result_date.strftime("%Y-%m-%d")

        raise ValueError(f"Invalid shift format: {shift}")
    
    @staticmethod
    def calculate_time(reference_time, shift):
        """
        reference time should be in YYYY-MM-DD HH:MM:SS format, output is also in this format
        shift has multiple supported format:
            (1) [+/-][x]H[y]M[z]S means x hours y minutes z seconds before/after reference time
                x,y,z could be any integer, '+' could be omitted, '0' could be omitted
                e.g.    -8H30M (8 hours 30 minutes before the reference time),
                        -2H30S (2 hours 30 seconds before the reference time)
                        1H (1 hour after the reference time),
                        +1M20S (1 minute 20 seconds after the reference time)
                        20H30M15S (20 hours 30 minutes 15 seconds after the reference time)

            (2) C12[Last/Next][xx/xx:xx/xx:xx:xx] means the nearest previous/next xx/xx:xx/xx:xx of the reference time under the 12-hour clock system
                xx/xx:xx/xx:xx:xx should be in range 00/00:00/00:00:00-11/11:59/11:59:59, the '0' on the left side could be emitted
                e.g.    C12Last[8/08/8:00/08:00/8:00:00/08:00:00] (return the nearest previous 8 o'clock of the reference time:
                                if reference time is 2024-01-07 10:30:00, then return 2024-01-07 08:00:00;
                                if reference time is 2024-01-07 07:30:00, then return 2024-01-06 20:00:00),
                        C12Next[10:30/10:30:00] (return the nearest next 10:30 of the reference time:
                                if reference time is 2024-01-07 08:00:00, then return 2024-01-07 10:30:00;
                                if reference time is 2024-01-07 11:30:00, then return 2024-01-07 22:30:00)
            (3) [/C24][Last/Next][xx/xx:xx/xx:xx:xx] means the nearest previous/next xx/xx:xx/xx:xx of the reference time under the 24-hour clock system
                xx/xx:xx/xx:xx:xx should be in range 00/00:00/00:00:00-23/23:59/23:59:59, the '0' on the left side could be emitted, 'C24' itself can also be omitted
                e.g.    C24Last[8/08/8:00/08:00/8:00:00/08:00:00] (return the nearest previous 8 o'clock of the reference time:
                                if reference time is 2024-01-07 10:30:00, then return 2024-01-07 08:00:00;
                                if reference time is 2024-01-07 07:30:00, then return 2024-01-06 08:00:00),
                        Next[10:30/10:30:00] (return the nearest next 10:30 of the reference time:
                                if reference time is 2024-01-07 08:00:00, then return 2024-01-07 10:30:00;
                                if reference time is 2024-01-07 11:30:00, then return 2024-01-08 10:30:00)


        """
        # Parse reference time
        ref_dt = datetime.strptime(reference_time, "%Y-%m-%d %H:%M:%S")

        # Mode 0: Simple time setting HH:MM or HH:MM:SS
        match = re.match(r'^(\d{1,2})(?::(\d{2}))?(?::(\d{2}))?$', shift)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            second = int(match.group(3)) if match.group(3) else 0

            # Validate time range
            if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                raise ValueError(f"Invalid time: {shift}")

            result_dt = ref_dt.replace(hour=hour, minute=minute, second=second)
            return result_dt.strftime("%Y-%m-%d %H:%M:%S")

        # Mode 1: [+/-][x]H[y]M[z]S
        match = re.match(r'^([+-]?)(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$', shift.upper())
        if match:
            sign_str = match.group(1)  # '+' or '-' or ''
            hours = int(match.group(2)) if match.group(2) else 0
            minutes = int(match.group(3)) if match.group(3) else 0
            seconds = int(match.group(4)) if match.group(4) else 0

            # Determine sign: default positive (+ can be omitted)
            sign = -1 if sign_str == '-' else 1

            delta = timedelta(hours=sign*hours, minutes=sign*minutes, seconds=sign*seconds)
            result_dt = ref_dt + delta
            return result_dt.strftime("%Y-%m-%d %H:%M:%S")

        # Mode 2: C12[Last/Next][time]
        match = re.match(r'^C12(Last|Next)(.+)$', shift, re.IGNORECASE)
        if match:
            direction = match.group(1).lower()
            time_str = match.group(2)
            return RelativeTimePrimitives._find_nearest_time_12h(ref_dt, time_str, direction)

        # Mode 3: [C24][Last/Next][time] or [Last/Next][time]
        match = re.match(r'^(?:C24)?(Last|Next)(.+)$', shift, re.IGNORECASE)
        if match:
            direction = match.group(1).lower()
            time_str = match.group(2)
            return RelativeTimePrimitives._find_nearest_time_24h(ref_dt, time_str, direction)

        raise ValueError(f"Invalid shift format: {shift}")

    @staticmethod
    def _parse_time_string(time_str):
        """Parse time string, return (hour, minute, second)"""
        # Supported formats: 8, 08, 8:00, 08:00, 8:00:00, 08:00:00
        parts = time_str.split(':')
        if len(parts) == 1:
            # Only hour
            hour = int(parts[0])
            minute = 0
            second = 0
        elif len(parts) == 2:
            # Hour:Minute
            hour = int(parts[0])
            minute = int(parts[1])
            second = 0
        elif len(parts) == 3:
            # Hour:Minute:Second
            hour = int(parts[0])
            minute = int(parts[1])
            second = int(parts[2])
        else:
            raise ValueError(f"Invalid time format: {time_str}")

        return hour, minute, second

    @staticmethod
    def _find_nearest_time_24h(ref_dt, time_str, direction):
        """Find nearest time in 24-hour format"""
        hour, minute, second = RelativeTimePrimitives._parse_time_string(time_str)

        # Validate time range
        if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
            raise ValueError(f"Invalid time {time_str} for 24-hour clock")

        # Create candidate time for today
        candidate = ref_dt.replace(hour=hour, minute=minute, second=second, microsecond=0)

        if direction == 'last':
            # Nearest previous time
            if candidate <= ref_dt:
                # Time today has passed or is exactly now
                return candidate.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Return yesterday's time
                candidate = candidate - timedelta(days=1)
                return candidate.strftime("%Y-%m-%d %H:%M:%S")
        else:  # 'next'
            # Nearest next time
            if candidate >= ref_dt:
                # Time today has not arrived yet or is exactly now
                return candidate.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Return tomorrow's time
                candidate = candidate + timedelta(days=1)
                return candidate.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _find_nearest_time_12h(ref_dt, time_str, direction):
        """Find nearest time in 12-hour format"""
        hour, minute, second = RelativeTimePrimitives._parse_time_string(time_str)

        # Validate time range (12-hour format: 0-11)
        if not (0 <= hour <= 11 and 0 <= minute <= 59 and 0 <= second <= 59):
            raise ValueError(f"Invalid time {time_str} for 12-hour clock")

        # Generate candidate times: AM (hour) and PM (hour+12)
        candidates = []

        # Consider a 3-day range to ensure finding the nearest time
        for day_offset in [-1, 0, 1]:
            base_date = ref_dt.date() + timedelta(days=day_offset)

            # AM time
            am_time = datetime.combine(base_date, datetime.min.time()).replace(
                hour=hour, minute=minute, second=second
            )
            candidates.append(am_time)

            # PM time (if hour is 0, 12 PM is 12:00, not 0:00)
            pm_hour = hour + 12 if hour != 0 else 12
            pm_time = datetime.combine(base_date, datetime.min.time()).replace(
                hour=pm_hour, minute=minute, second=second
            )
            candidates.append(pm_time)

        # Filter candidate times based on direction
        if direction == 'last':
            # All past or present candidate times
            valid_candidates = [c for c in candidates if c <= ref_dt]
            if valid_candidates:
                # Choose the nearest (largest timestamp)
                nearest = max(valid_candidates)
                return nearest.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # No past candidate times, choose the furthest past (theoretically shouldn't happen)
                nearest = max(candidates)  # Choose the largest (closest to future)
                return nearest.strftime("%Y-%m-%d %H:%M:%S")
        else:  # 'next'
            # All future or present candidate times
            valid_candidates = [c for c in candidates if c >= ref_dt]
            if valid_candidates:
                # Choose the nearest (smallest timestamp)
                nearest = min(valid_candidates)
                return nearest.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # No future candidate times, choose the furthest future (theoretically shouldn't happen)
                nearest = min(candidates)  # Choose the smallest (closest to past)
                return nearest.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def calculate_datetime(reference_datetime, shift):
        """
        reference_datetime should be in YYYY-MM-DD HH:MM:SS format, output is also in this format
        shift is combination of the calculate_date shift and calculate_time shift:
            e.g.    "0w1 9:00" (09:00:00 of this week's Monday)
                    "1m5 10:30:19" (10:30:19 of the 5th day of the 1st month after the reference date's month)
                    "1D Next8" (calculate C24Next08:00:00 first, then caluclate +1D)
        """
        # Parse reference datetime
        ref_dt = datetime.strptime(reference_datetime, "%Y-%m-%d %H:%M:%S")

        # Split shift string into date part and time part
        parts = shift.strip().split()
        if len(parts) != 2:
            raise ValueError(f"Invalid shift format for datetime: {shift}. Expected two parts separated by space.")

        date_shift, time_shift = parts[0], parts[1]

        # Check if time part needs to be processed first (if time part contains Last/Next)
        time_first = False
        time_first_patterns = [r'^(C12|C24)?(Last|Next)', r'^(Last|Next)']
        for pattern in time_first_patterns:
            if re.match(pattern, time_shift, re.IGNORECASE):
                time_first = True
                break

        if time_first:
            # Process time part first, then date part
            # Apply time shift
            intermediate_datetime = RelativeTimePrimitives.calculate_time(
                ref_dt.strftime("%Y-%m-%d %H:%M:%S"),
                time_shift
            )
            # Apply date shift
            intermediate_date = datetime.strptime(intermediate_datetime, "%Y-%m-%d %H:%M:%S")
            result_date_str = RelativeTimePrimitives.calculate_date(
                intermediate_date.strftime("%Y-%m-%d"),
                date_shift
            )
            # Keep time part unchanged
            result_dt = datetime.strptime(result_date_str, "%Y-%m-%d").replace(
                hour=intermediate_date.hour,
                minute=intermediate_date.minute,
                second=intermediate_date.second
            )
        else:
            # Process date part first, then time part
            # Apply date shift
            result_date_str = RelativeTimePrimitives.calculate_date(
                ref_dt.strftime("%Y-%m-%d"),
                date_shift
            )
            # Combine date and original time
            intermediate_datetime = f"{result_date_str} {ref_dt.strftime('%H:%M:%S')}"
            # Apply time shift
            result_dt_str = RelativeTimePrimitives.calculate_time(intermediate_datetime, time_shift)
            result_dt = datetime.strptime(result_dt_str, "%Y-%m-%d %H:%M:%S")

        return result_dt.strftime("%Y-%m-%d %H:%M:%S")
    @staticmethod
    def compare_datetime(target, source):
        """
        if target is in YYYY-mm-DD format, source could be YYYY-mm-DD, YYYY-mm-DD HH:MM or YYYY-mm-DD HH:MM:SS (time part will be ignored), compare date difference and return the absolute value in seconds
        if target is in HH:MM:SS or HH:MM format, source could be HH:MM:SS, HH:MM, YYYY-mm-DD HH:MM or YYYY-mm-DD HH:MM:SS (date part will be ignored), compare time difference and return the absolute value in seconds
        if target is in YYYY-mm-DD HH:MM or YYYY-mm-DD HH:MM:SS format, source could be YYYY-mm-DD HH:MM or YYYY-mm-DD HH:MM:SS, compare datetime difference and return the absolute value in seconds
        all unassigned SS will be 00
        """
        def parse_datetime_or_date(s):
            """Parse string, return datetime object. If only date, time set to 0; if only time, date set to 1900-01-01 (ignored)"""
            try:
                # Try to parse as full datetime
                return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    # Try to parse as datetime HH:MM
                    return datetime.strptime(s, "%Y-%m-%d %H:%M")
                except ValueError:
                    try:
                        # Try to parse as date
                        return datetime.strptime(s, "%Y-%m-%d")
                    except ValueError:
                        try:
                            # Try to parse as time HH:MM:SS
                            return datetime.strptime(s, "%H:%M:%S")
                        except ValueError:
                            try:
                                # Try to parse as time HH:MM
                                return datetime.strptime(s, "%H:%M")
                            except ValueError:
                                raise ValueError(f"Cannot parse time format: {s}")

        # Parse target and source
        target_dt = parse_datetime_or_date(target)
        source_dt = parse_datetime_or_date(source)

        # Determine comparison mode
        target_has_date = '-' in target
        target_has_time = ':' in target

        # If target has only date, ignore time part
        if target_has_date and not target_has_time:
            # Compare date parts of target and source, set time to 0
            target_date = target_dt.date()
            source_date = source_dt.date()
            # Calculate date difference (days) converted to seconds
            delta = abs((target_date - source_date).total_seconds())
            return delta

        # If target has only time, ignore date part
        if not target_has_date and target_has_time:
            # Compare time parts of target and source, set date to same (use arbitrary date, e.g., 1900-01-01)
            target_time = target_dt.time()
            source_time = source_dt.time()
            # Create datetime objects with same date to calculate time difference
            base_date = datetime(1900, 1, 1).date()
            target_dt2 = datetime.combine(base_date, target_time)
            source_dt2 = datetime.combine(base_date, source_time)
            delta = abs((target_dt2 - source_dt2).total_seconds())
            return delta

        # If target has date and time, perform full datetime comparison
        if target_has_date and target_has_time:
            # source might also have only date or time, but parse_datetime_or_date has handled it
            delta = abs((target_dt - source_dt).total_seconds())
            return delta

        # Should not reach here
        raise ValueError(f"Cannot compare format: target={target}, source={source}")