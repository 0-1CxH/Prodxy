import yaml
import random
from typing import List, Dict
from datetime import datetime, date, time, timedelta
from dataclasses import dataclass

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
    def date(boundary, is_sequential=True, count=1):
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
        elif isinstance(boundary, int):
            end_date = start_date + timedelta(days=boundary)
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

@dataclass
class ProdxyPropertyItem:
    item_name: str
    weight: float|int = 1.0

@dataclass
class ProdxyPropertyCategory:
    category_name: str
    items: List[ProdxyPropertyItem]
    weight: float|int = 1.0
    
@dataclass
class ProdxyProperty:
    property_name: str
    categories: List[ProdxyPropertyCategory]

@dataclass
class PropertyIndicator:
    property_name: str
    category_name: str = None
    item_name: str = None

    def __dict__(self):
        ret = {"property_name": self.property_name}
        if self.category_name is not None:
            ret.update({"category_name": self.category_name})
        if self.item_name is not None:
            ret.update({"item_name": self.item_name})
        return ret
    
    def value(self):
        ret = self.property_name
        if self.category_name is not None:
            ret = self.category_name
        if self.item_name is not None:
            ret = self.item_name
        return ret

@dataclass
class ProdxyConstrain:
    constrain_subject: PropertyIndicator
    constrain_object: List[PropertyIndicator]

@dataclass
class ProdxyPropertyLibraryConfig:
    properties: List[ProdxyProperty]
    constrains: List[ProdxyConstrain]

class ProdxyPropertyLibrary:
    def __init__(self, config: ProdxyPropertyLibraryConfig):
        self.properties = config.properties
        self.constrains = config.constrains
        self._property_map = {prop.property_name: prop for prop in self.properties}

    @classmethod
    def load_from_dict(cls, data):
        """Load configuration from dictionary"""
        properties = []

        # Parse properties
        for prop_data in data.get("properties", []):
            categories = []

            # Parse categories
            for cat_data in prop_data.get("categories", []):
                items = []

                # Parse items
                for item_data in cat_data.get("items", []):
                    item = ProdxyPropertyItem(
                        item_name=item_data["item_name"],
                        weight=item_data.get("weight", 1.0)
                    )
                    items.append(item)

                category = ProdxyPropertyCategory(
                    category_name=cat_data["category_name"],
                    items=items,
                    weight=cat_data.get("weight", 1.0)
                )
                categories.append(category)

            property = ProdxyProperty(
                property_name=prop_data["property_name"],
                categories=categories
            )
            properties.append(property)

        # Parse constraints
        constrains = []
        for constrain_data in data.get("constrains", []):
            subject_data = constrain_data["constrain_subject"]
            subject = PropertyIndicator(
                property_name=subject_data["property_name"],
                category_name=subject_data.get("category_name"),
                item_name=subject_data.get("item_name")
            )

            objects = []
            for obj_data in constrain_data["constrain_object"]:
                obj = PropertyIndicator(
                    property_name=obj_data["property_name"],
                    category_name=obj_data.get("category_name"),
                    item_name=obj_data.get("item_name")
                )
                objects.append(obj)

            constrain = ProdxyConstrain(
                constrain_subject=subject,
                constrain_object=objects
            )
            constrains.append(constrain)

        config = ProdxyPropertyLibraryConfig(
            properties=properties,
            constrains=constrains
        )

        return cls(config)

    @classmethod
    def load_from_yaml(cls, yaml_path: str):
        """Load configuration from YAML file"""
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
        return cls.load_from_dict(data)

    def _get_property(self, property_name):
        """Get property by name, raise ValueError if not found"""
        if property_name not in self._property_map:
            raise ValueError(f"Property '{property_name}' not found")
        return self._property_map[property_name]

    def _get_category(self, property_name, category_name):
        """Get category by property and category names, raise ValueError if not found"""
        prop = self._get_property(property_name)
        for category in prop.categories:
            if category.category_name == category_name:
                return category
        raise ValueError(f"Category '{category_name}' not found in property '{property_name}'")

    def _apply_category_constraints(self, property_name, available_categories):
        """Apply constraints to filter available categories"""
        # For now, return all categories (constraint logic to be implemented later)
        return available_categories

    def _apply_item_constraints(self, property_name, category_name, available_items):
        """Apply constraints to filter available items"""
        # For now, return all items (constraint logic to be implemented later)
        return available_items

    def sample_categories(self, property_name, count=1, allow_repeat=False) -> List[PropertyIndicator]:
        """Sample categories by given property_name with constraints on categories"""
        prop = self._get_property(property_name)

        # Get available categories after applying constraints
        available_categories = self._apply_category_constraints(property_name, prop.categories)

        if not available_categories:
            raise ValueError(f"No available categories for property '{property_name}' after applying constraints")

        # Prepare items and weights for sampling
        category_names = [cat.category_name for cat in available_categories]
        weights = [cat.weight for cat in available_categories]

        # Use ValueGeneratorPrimitives.enum for sampling
        sampled_categories = ValueGeneratorPrimitives.enum(
            dict(zip(category_names, weights)),
            count=count,
            allow_repeat=allow_repeat
        )

        # Convert to PropertyIndicator objects
        indicators = []
        for category_name in sampled_categories:
            indicator = PropertyIndicator(
                property_name=property_name,
                category_name=category_name
            )
            indicators.append(indicator)

        return indicators

    def sample_items(self, property_name, category_name, count=1, allow_repeat=False) -> List[PropertyIndicator]:
        """Sample items by given property_name and category_name with constraints on items and categories"""
        category = self._get_category(property_name, category_name)

        # Get available items after applying constraints
        available_items = self._apply_item_constraints(property_name, category_name, category.items)

        if not available_items:
            raise ValueError(f"No available items for property '{property_name}', category '{category_name}' after applying constraints")

        # Prepare items and weights for sampling
        item_names = [item.item_name for item in available_items]
        weights = [item.weight for item in available_items]

        # Use ValueGeneratorPrimitives.enum for sampling
        sampled_items = ValueGeneratorPrimitives.enum(
            dict(zip(item_names, weights)),
            count=count,
            allow_repeat=allow_repeat
        )

        # Convert to PropertyIndicator objects
        indicators = []
        for item_name in sampled_items:
            indicator = PropertyIndicator(
                property_name=property_name,
                category_name=category_name,
                item_name=item_name
            )
            indicators.append(indicator)

        return indicators
    
    def sample(self, property_name, category_name=None, count=1, allow_repeat=False, none_prob=0.0, random_category=False):
        if none_prob > 0:
            if random.random() < none_prob:
                return None
        if random_category is False:
            if category_name is None:
                ret = self.sample_categories(property_name, count=count, allow_repeat=allow_repeat)
            else:
                ret = self.sample_items(property_name, category_name, count=count, allow_repeat=allow_repeat)
        else:
            ret = []
            for c in range(count):
                category_name = self.sample_categories(property_name, count=1, allow_repeat=False)[0].category_name
                ret.append(self.sample_items(property_name, category_name, count=1, allow_repeat=False)[0])
        
        ret = [_.value() for _ in ret]
        if len(ret) == 1:
            return ret[0]
        else:
            return ret

    
