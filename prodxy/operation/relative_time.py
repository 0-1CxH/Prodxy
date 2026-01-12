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
        # 解析参考日期
        ref_date = datetime.strptime(reference_date, "%Y-%m-%d")

        # 模式1: [+/-x]D
        match = re.match(r'^([+-]?\d+)D$', shift)
        if match:
            days = int(match.group(1))
            result_date = ref_date + timedelta(days=days)
            return result_date.strftime("%Y-%m-%d")

        # 模式2: [+/-x]m[+/-y]
        match = re.match(r'^([+-]?\d+)m([+-]?\d+)$', shift)
        if match:
            months = int(match.group(1))
            day_offset = int(match.group(2))

            # 计算目标年月
            year = ref_date.year + (ref_date.month + months - 1) // 12
            month = (ref_date.month + months) % 12
            if month == 0:
                month = 12

            # 获取该月的天数
            _, days_in_month = monthrange(year, month)

            # 计算目标日期
            if day_offset >= 0:
                # 从月初开始计数 (1-based)
                target_day = day_offset
            else:
                # 从月末开始倒数计数
                # day_offset = -1 表示最后一天，-2 表示倒数第二天，以此类推
                target_day = days_in_month + day_offset + 1

            # 确保目标日期在有效范围内
            if 1 <= target_day <= days_in_month:
                result_date = datetime(year, month, target_day)
                return result_date.strftime("%Y-%m-%d")
            else:
                raise ValueError(f"Day offset {day_offset} out of range for month {year}-{month:02d}")

        # 模式3: [+/-x]w[y]
        match = re.match(r'^([+-]?\d+)w([1-7])$', shift)
        if match:
            weeks = int(match.group(1))
            weekday = int(match.group(2))  # 1=Monday, ..., 7=Sunday

            # 计算目标周的周一
            # ref_date的weekday: 0=Monday, ..., 6=Sunday
            ref_weekday = ref_date.weekday()  # 0-6 (Monday=0)
            days_to_monday = ref_weekday  # 距离本周一的天数
            monday_of_ref_week = ref_date - timedelta(days=days_to_monday)

            # 计算目标周的周一
            target_monday = monday_of_ref_week + timedelta(weeks=weeks)

            # 计算目标日期 (weekday: 1=Monday, ..., 7=Sunday)
            result_date = target_monday + timedelta(days=weekday-1)
            return result_date.strftime("%Y-%m-%d")

        # 模式4: [Last/Next]w[y]
        match = re.match(r'^(Last|Next)w([1-7])$', shift, re.IGNORECASE)
        if match:
            direction = match.group(1).lower()
            weekday = int(match.group(2))  # 1=Monday, ..., 7=Sunday

            # ref_date的weekday: 0=Monday, ..., 6=Sunday
            ref_weekday = ref_date.weekday() + 1  # 转换为1-7 (Monday=1)

            if direction == 'last':
                # 最近的上一个周几
                if ref_weekday >= weekday:
                    # 本周的周几
                    days_diff = ref_weekday - weekday
                    result_date = ref_date - timedelta(days=days_diff)
                else:
                    # 上周的周几
                    days_diff = weekday - ref_weekday
                    result_date = ref_date - timedelta(days=7 - days_diff)
            else:  # 'next'
                # 最近的下一个周几
                if ref_weekday <= weekday:
                    # 本周的周几
                    days_diff = weekday - ref_weekday
                    result_date = ref_date + timedelta(days=days_diff)
                else:
                    # 下周的周几
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
        # 解析参考时间
        ref_dt = datetime.strptime(reference_time, "%Y-%m-%d %H:%M:%S")

        # 模式0: 简单时间设置 HH:MM 或 HH:MM:SS
        match = re.match(r'^(\d{1,2})(?::(\d{2}))?(?::(\d{2}))?$', shift)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            second = int(match.group(3)) if match.group(3) else 0

            # 验证时间范围
            if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                raise ValueError(f"Invalid time: {shift}")

            result_dt = ref_dt.replace(hour=hour, minute=minute, second=second)
            return result_dt.strftime("%Y-%m-%d %H:%M:%S")

        # 模式1: [+/-][x]H[y]M[z]S
        match = re.match(r'^([+-]?)(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$', shift.upper())
        if match:
            sign_str = match.group(1)  # '+' or '-' or ''
            hours = int(match.group(2)) if match.group(2) else 0
            minutes = int(match.group(3)) if match.group(3) else 0
            seconds = int(match.group(4)) if match.group(4) else 0

            # 确定符号：默认正数（+可省略）
            sign = -1 if sign_str == '-' else 1

            delta = timedelta(hours=sign*hours, minutes=sign*minutes, seconds=sign*seconds)
            result_dt = ref_dt + delta
            return result_dt.strftime("%Y-%m-%d %H:%M:%S")

        # 模式2: C12[Last/Next][time]
        match = re.match(r'^C12(Last|Next)(.+)$', shift, re.IGNORECASE)
        if match:
            direction = match.group(1).lower()
            time_str = match.group(2)
            return RelativeTimePrimitives._find_nearest_time_12h(ref_dt, time_str, direction)

        # 模式3: [C24][Last/Next][time] 或 [Last/Next][time]
        match = re.match(r'^(?:C24)?(Last|Next)(.+)$', shift, re.IGNORECASE)
        if match:
            direction = match.group(1).lower()
            time_str = match.group(2)
            return RelativeTimePrimitives._find_nearest_time_24h(ref_dt, time_str, direction)

        raise ValueError(f"Invalid shift format: {shift}")

    @staticmethod
    def _parse_time_string(time_str):
        """解析时间字符串，返回 (小时, 分钟, 秒)"""
        # 支持格式: 8, 08, 8:00, 08:00, 8:00:00, 08:00:00
        parts = time_str.split(':')
        if len(parts) == 1:
            # 只有小时
            hour = int(parts[0])
            minute = 0
            second = 0
        elif len(parts) == 2:
            # 小时:分钟
            hour = int(parts[0])
            minute = int(parts[1])
            second = 0
        elif len(parts) == 3:
            # 小时:分钟:秒
            hour = int(parts[0])
            minute = int(parts[1])
            second = int(parts[2])
        else:
            raise ValueError(f"Invalid time format: {time_str}")

        return hour, minute, second

    @staticmethod
    def _find_nearest_time_24h(ref_dt, time_str, direction):
        """24小时制最近时间查找"""
        hour, minute, second = RelativeTimePrimitives._parse_time_string(time_str)

        # 验证时间范围
        if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
            raise ValueError(f"Invalid time {time_str} for 24-hour clock")

        # 创建今天的候选时间
        candidate = ref_dt.replace(hour=hour, minute=minute, second=second, microsecond=0)

        if direction == 'last':
            # 最近的上一个时间
            if candidate <= ref_dt:
                # 今天的时间已经过去或正好是现在
                return candidate.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # 返回昨天的时间
                candidate = candidate - timedelta(days=1)
                return candidate.strftime("%Y-%m-%d %H:%M:%S")
        else:  # 'next'
            # 最近的下一个时间
            if candidate >= ref_dt:
                # 今天的时间还未到来或正好是现在
                return candidate.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # 返回明天的时间
                candidate = candidate + timedelta(days=1)
                return candidate.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _find_nearest_time_12h(ref_dt, time_str, direction):
        """12小时制最近时间查找"""
        hour, minute, second = RelativeTimePrimitives._parse_time_string(time_str)

        # 验证时间范围 (12小时制: 0-11)
        if not (0 <= hour <= 11 and 0 <= minute <= 59 and 0 <= second <= 59):
            raise ValueError(f"Invalid time {time_str} for 12-hour clock")

        # 生成候选时间: 上午 (hour) 和下午 (hour+12)
        candidates = []

        # 考虑三天的范围以确保找到最近的时间
        for day_offset in [-1, 0, 1]:
            base_date = ref_dt.date() + timedelta(days=day_offset)

            # 上午时间
            am_time = datetime.combine(base_date, datetime.min.time()).replace(
                hour=hour, minute=minute, second=second
            )
            candidates.append(am_time)

            # 下午时间 (如果hour为0，下午12点就是12:00，不是0:00)
            pm_hour = hour + 12 if hour != 0 else 12
            pm_time = datetime.combine(base_date, datetime.min.time()).replace(
                hour=pm_hour, minute=minute, second=second
            )
            candidates.append(pm_time)

        # 根据方向筛选候选时间
        if direction == 'last':
            # 所有过去或现在的候选时间
            valid_candidates = [c for c in candidates if c <= ref_dt]
            if valid_candidates:
                # 选择最接近的（最大的时间戳）
                nearest = max(valid_candidates)
                return nearest.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # 没有过去的候选时间，选择最远的过去（理论上不会发生）
                nearest = max(candidates)  # 选择最大的（最接近未来的）
                return nearest.strftime("%Y-%m-%d %H:%M:%S")
        else:  # 'next'
            # 所有未来或现在的候选时间
            valid_candidates = [c for c in candidates if c >= ref_dt]
            if valid_candidates:
                # 选择最接近的（最小的时间戳）
                nearest = min(valid_candidates)
                return nearest.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # 没有未来的候选时间，选择最远的未来（理论上不会发生）
                nearest = min(candidates)  # 选择最小的（最接近过去的）
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
        # 解析参考日期时间
        ref_dt = datetime.strptime(reference_datetime, "%Y-%m-%d %H:%M:%S")

        # 分割shift字符串为日期部分和时间部分
        parts = shift.strip().split()
        if len(parts) != 2:
            raise ValueError(f"Invalid shift format for datetime: {shift}. Expected two parts separated by space.")

        date_shift, time_shift = parts[0], parts[1]

        # 检查是否需要先处理时间部分（如果时间部分包含 Last/Next）
        time_first = False
        time_first_patterns = [r'^(C12|C24)?(Last|Next)', r'^(Last|Next)']
        for pattern in time_first_patterns:
            if re.match(pattern, time_shift, re.IGNORECASE):
                time_first = True
                break

        if time_first:
            # 先处理时间部分，再处理日期部分
            # 应用时间shift
            intermediate_datetime = RelativeTimePrimitives.calculate_time(
                ref_dt.strftime("%Y-%m-%d %H:%M:%S"),
                time_shift
            )
            # 应用日期shift
            intermediate_date = datetime.strptime(intermediate_datetime, "%Y-%m-%d %H:%M:%S")
            result_date_str = RelativeTimePrimitives.calculate_date(
                intermediate_date.strftime("%Y-%m-%d"),
                date_shift
            )
            # 保持时间部分不变
            result_dt = datetime.strptime(result_date_str, "%Y-%m-%d").replace(
                hour=intermediate_date.hour,
                minute=intermediate_date.minute,
                second=intermediate_date.second
            )
        else:
            # 先处理日期部分，再处理时间部分
            # 应用日期shift
            result_date_str = RelativeTimePrimitives.calculate_date(
                ref_dt.strftime("%Y-%m-%d"),
                date_shift
            )
            # 组合日期和原始时间
            intermediate_datetime = f"{result_date_str} {ref_dt.strftime('%H:%M:%S')}"
            # 应用时间shift
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
            """解析字符串，返回datetime对象。如果只有日期，时间设为0；如果只有时间，日期设为1900-01-01（忽略）"""
            try:
                # 尝试解析为完整日期时间
                return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    # 尝试解析为日期时间 HH:MM
                    return datetime.strptime(s, "%Y-%m-%d %H:%M")
                except ValueError:
                    try:
                        # 尝试解析为日期
                        return datetime.strptime(s, "%Y-%m-%d")
                    except ValueError:
                        try:
                            # 尝试解析为时间 HH:MM:SS
                            return datetime.strptime(s, "%H:%M:%S")
                        except ValueError:
                            try:
                                # 尝试解析为时间 HH:MM
                                return datetime.strptime(s, "%H:%M")
                            except ValueError:
                                raise ValueError(f"无法解析时间格式: {s}")

        # 解析target和source
        target_dt = parse_datetime_or_date(target)
        source_dt = parse_datetime_or_date(source)

        # 确定比较模式
        target_has_date = '-' in target
        target_has_time = ':' in target

        # 如果target只有日期，则忽略时间部分
        if target_has_date and not target_has_time:
            # 将target和source的日期部分进行比较，时间设为0
            target_date = target_dt.date()
            source_date = source_dt.date()
            # 计算日期差（天数）转换为秒
            delta = abs((target_date - source_date).total_seconds())
            return delta

        # 如果target只有时间，则忽略日期部分
        if not target_has_date and target_has_time:
            # 将target和source的时间部分进行比较，日期设为相同（使用任意日期，如1900-01-01）
            target_time = target_dt.time()
            source_time = source_dt.time()
            # 创建相同日期的datetime对象以计算时间差
            base_date = datetime(1900, 1, 1).date()
            target_dt2 = datetime.combine(base_date, target_time)
            source_dt2 = datetime.combine(base_date, source_time)
            delta = abs((target_dt2 - source_dt2).total_seconds())
            return delta

        # 如果target有日期和时间，则进行完整日期时间比较
        if target_has_date and target_has_time:
            # source也可能只有日期或时间，但parse_datetime_or_date已经处理了
            delta = abs((target_dt - source_dt).total_seconds())
            return delta

        # 不应该到达这里
        raise ValueError(f"无法比较格式: target={target}, source={source}")