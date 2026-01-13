import random
from datetime import datetime, date, time, timedelta

class ValueGeneratorPrimitives:
    @staticmethod
    def enum(classifications, count=1, allow_repeat=False):
        # classifications could be tuple, list, set(equal weights to all values) or dict(values are weights)
        # count means how many values to generate, if not allow repeat, count should be less than or equal to the number of classifications
        # allow_repeat means whether to allow repeat values
        
        items = []
        weights = None
        
        if isinstance(classifications, dict):
            items = list(classifications.keys())
            weights = list(classifications.values())
        elif isinstance(classifications, (list, tuple, set)):
            items = list(classifications)
        else:
            raise ValueError("classifications must be list, tuple, set or dict")
            
        if not items:
            return []
            
        if allow_repeat:
            if weights:
                return random.choices(items, weights=weights, k=count)
            else:
                return random.choices(items, k=count)
        else:
            if count > len(items):
                raise ValueError(f"Cannot generate {count} unique values from {len(items)} items")
            
            if weights:
                # Weighted sampling without replacement (Efraimidis-Spirakis algorithm)
                scored_items = []
                for item, weight in zip(items, weights):
                    if weight > 0:
                        score = random.random() ** (1.0 / weight)
                        scored_items.append((score, item))
                scored_items.sort(reverse=True, key=lambda x: x[0])
                return [item for score, item in scored_items[:count]]
            else:
                return random.sample(items, count)
    
    @staticmethod
    def range(boundary, is_integer, count=1, allow_repeat=False):
        # boundary could be int or float
        # is_integer means whether the values should be integers
        # count means how many values to generate
        # allow_repeat means whether to allow repeat values
        
        start = 0
        end = 0
        
        if isinstance(boundary, (list, tuple)):
            if len(boundary) != 2:
                raise ValueError("boundary list/tuple must have 2 elements")
            start = boundary[0]
            end = boundary[1]
        else:
            end = boundary
            
        if start > end:
            start, end = end, start
            
        if is_integer:
            start = int(start)
            end = int(end)
            if allow_repeat:
                return [random.randint(start, end) for _ in range(count)]
            else:
                # random.sample range is exclusive on stop, so end+1
                population = range(start, end + 1)
                if count > len(population):
                     raise ValueError(f"Cannot generate {count} unique integers from range {start}-{end}")
                return random.sample(population, count)
        else:
            # float
            return [random.uniform(start, end) for _ in range(count)]
    
    @staticmethod
    def date(boundary, is_sequential, count=1):
        # boundary could be datetime or date (in YYYY-mm-DD format)
        # is_sequential means whether the values should be sequential (x+1-th is later than x-th)
        # count means how many values to generate
        
        def parse_date(d):
            if isinstance(d, str):
                return datetime.strptime(d, "%Y-%m-%d").date()
            elif isinstance(d, datetime):
                return d.date()
            elif isinstance(d, date):
                return d
            raise ValueError(f"Invalid date format: {d}")

        start_date = date.today()
        end_date = start_date
        
        if isinstance(boundary, (list, tuple)):
            start_date = parse_date(boundary[0])
            end_date = parse_date(boundary[1])
        else:
            end_date = parse_date(boundary)
            # If single boundary, determine range relative to today
            if end_date < start_date:
                start_date, end_date = end_date, start_date
            # else: start_date is today, end_date is boundary
        
        if start_date > end_date:
             start_date, end_date = end_date, start_date
             
        delta_days = (end_date - start_date).days
        
        generated_dates = []
        for _ in range(count):
            random_days = random.randint(0, delta_days)
            res_date = start_date + timedelta(days=random_days)
            generated_dates.append(res_date)
            
        if is_sequential:
            generated_dates.sort()
            
        return [d.strftime("%Y-%m-%d") for d in generated_dates]
    
    @staticmethod
    def time(boundary, is_sequential, count=1):
        # boundary could be time or datetime (in HH:MM:SS format)
        # is_sequential means whether the values should be sequential (x+1-th is later than x-th)
        # count means how many values to generate
        
        def parse_time_seconds(t):
            # Return seconds from midnight
            if isinstance(t, str):
                try:
                    dt = datetime.strptime(t, "%H:%M:%S")
                except ValueError:
                    try:
                        dt = datetime.strptime(t, "%H:%M")
                    except ValueError:
                         raise ValueError(f"Invalid time format: {t}")
                return dt.hour * 3600 + dt.minute * 60 + dt.second
            elif isinstance(t, datetime):
                return t.hour * 3600 + t.minute * 60 + t.second
            elif isinstance(t, time):
                return t.hour * 3600 + t.minute * 60 + t.second
            elif isinstance(t, (int, float)):
                return int(t)
            raise ValueError(f"Invalid time format: {t}")

        start_seconds = 0
        end_seconds = 24 * 3600 - 1
        
        if isinstance(boundary, (list, tuple)):
            start_seconds = parse_time_seconds(boundary[0])
            end_seconds = parse_time_seconds(boundary[1])
        else:
            end_seconds = parse_time_seconds(boundary)
            
        if start_seconds > end_seconds:
            start_seconds, end_seconds = end_seconds, start_seconds
            
        generated_times = []
        for _ in range(count):
            random_sec = random.randint(start_seconds, end_seconds)
            m, s = divmod(random_sec, 60)
            h, m = divmod(m, 60)
            generated_times.append(time(hour=h, minute=m, second=s))
            
        if is_sequential:
            generated_times.sort()
            
        return [t.strftime("%H:%M:%S") for t in generated_times]
