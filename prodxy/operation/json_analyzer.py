import json
import jsonpath_ng
import functools

class JsonPathAnalyzer:

    @staticmethod
    @functools.lru_cache(maxsize=512) # Need this LRU cache to speed up 500x times
    def parse(jsonpath_str):
        return jsonpath_ng.parse(jsonpath_str)
    
    @staticmethod
    def get(d, jsonpath_str):
        jsonpath_parser = JsonPathAnalyzer.parse(jsonpath_str)
        matches = jsonpath_parser.find(d)
        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return matches[0].value
        else:
            return [match.value for match in matches]
    
    @staticmethod
    def set(d, jsonpath_str, value, on_index=None):
        if on_index is None:
            jsonpath_parser = JsonPathAnalyzer.parse(jsonpath_str)
            jsonpath_parser.update(d, value)
        else:
            # reg on_index to list
            if isinstance(on_index, int):
                on_index = [on_index]
            if not isinstance(on_index, list):
                return
            
            jsonpath_parser = JsonPathAnalyzer.parse(jsonpath_str)
            matches = jsonpath_parser.find(d)

            # if no match
            if len(matches) == 0:
                return
            # if matched one elem
            elif len(matches) == 1:
                if isinstance(matches[0].value, list): # set the sub elem by indices if is list
                    for index in on_index:
                        if index < len(matches[0].value):
                            matches[0].value[index] = value
                else: # set the elem if is not list
                    matches[0].full_path.update(d, value)
            # if matched multiple elems
            else:
                for index in on_index:
                    if index < len(matches):
                        matches[index].full_path.update(d, value)


class JsonPathDict:
    def __init__(self, d):
        self.d = d
        self.loaded_from = None
    
    @classmethod
    def load(cls, path):
        with open(path, 'r') as f:
            if path.endswith('.jsonl'):
                obj = cls([json.loads(line) for line in f])
                obj.loaded_from = path
                return obj
            elif path.endswith('.json'):
                obj = cls(json.load(f))
                obj.loaded_from = path
                return obj
            else:
                raise ValueError("Unsupported file format")
    
    def dump(self, path=None):
        if path is None:
            path = self.loaded_from
        if path is None:
            raise ValueError("Path not specified")
        with open(path, 'w') as f:
            if path.endswith('.jsonl'):
                for line in self.d:
                    json.dump(line, f, ensure_ascii=False)
                    f.write('\n')
            elif path.endswith('.json'):
                json.dump(self.d, f, ensure_ascii=False)
            else:
                raise ValueError("Unsupported file format")

    
    def __getitem__(self, key):
        return JsonPathAnalyzer.get(self.d, key)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            JsonPathAnalyzer.set(self.d, key, value)
        elif isinstance(key, tuple):
            key, *on_index = key
            JsonPathAnalyzer.set(self.d, key, value, on_index=on_index)
        else:
            raise TypeError("Key must be a string or a tuple")

    def __delitem__(self, key):
        JsonPathAnalyzer.set(self.d, key, None)

    def __contains__(self, key):
        return JsonPathAnalyzer.get(self.d, key) is not None
    
    def __iter__(self):
        return iter(self.d)

    def __len__(self):
        return len(self.d)

    def __repr__(self):
        return repr(self.d)

    def __str__(self):
        return str(self.d)


class FieldCentricAnalyzer:
    """
    Field-centric analyzer for querying lists of dictionaries.
    """
    # e.g.
    # data = FieldCentricAnalyzer([
    #   {"a": 1, "b": 2, "c": 3},
    #   {"a": 1, "b": 3, "c": 4, "d": 1},
    #   {"a": 2, "b": 3, "c": 4},
    #   {"a": 2, "b": 4, "c": 5, "d": 2},
    # ])
    # data.a(1) -> FieldCentricAnalyzer([{"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 3, "c": 4}])
    # data.a(1)[0] -> FieldCentricAnalyzer([{"a": 1, "b": 2, "c": 3}])
    # data.b(3) = data.b(3, "eq") -> FieldCentricAnalyzer([{"a": 1, "b": 3, "c": 4}, {"a": 2, "b": 3, "c": 4}]) # return those that field b==3
    # data.b(3, "gt") -> FieldCentricAnalyzer([{"a": 2, "b": 4, "c": 5}]) # return those that field b>3
    # data.d("*") -> FieldCentricAnalyzer([{"a": 1, "b": 3, "c": 4, "d": 1}, {"a": 2, "b": 4, "c": 5, "d": 2}]) # only return those with field "d"
    # data.a(3) -> FieldCentricAnalyzer([])
    # data.a(3)[2] -> None
    # data.a -> FieldCentricAnalyzer([1, 1, 2, 2])
    # data.a[2] -> 2
    # data.d -> FieldCentricAnalyzer([1, 2])
    # data.d[2] -> None
    # for group_name, group_values in data.a:
    #     group_name -> 1, group_values -> FieldCentricAnalyzer([{"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 3, "c": 4}]);
    #     group_name -> 2, group_values -> FieldCentricAnalyzer([{"a": 2, "b": 3, "c": 4}, {"a": 2, "b": 4, "c": 5, "d": 2}]);
    # for value in data.a(1):
    #     value -> {"a": 1, "b": 2, "c": 3}
    #     value -> {"a": 1, "b": 3, "c": 4, "d": 1}
    def __init__(self, data):
        """
        data: list of dictionaries
        """
        self._data = data  # list of dicts
        self._mode = "dicts"  # "dicts" or "values"
        self._field_name = None  # field name if in values mode
        self._parent = None  # parent analyzer if in values mode
    
    def __len__(self):
        return len(self._data)

    def __getattr__(self, name):
        # Return a new analyzer with values of field across dicts
        if self._mode == "dicts":
            # Extract values for this field, skipping dicts without the field
            values = []
            for d in self._data:
                if name in d:
                    values.append(d[name])
            # Create value-mode analyzer
            analyzer = FieldCentricAnalyzer(values)
            analyzer._mode = "values"
            analyzer._field_name = name
            analyzer._parent = self
            return analyzer
        else:
            # In values mode, attribute access not defined
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __call__(self, value, op="eq"):
        if self._mode == "values" and self._parent is not None:
            # Filter parent dicts based on field value
            field_name = self._field_name
            if value == "*":
                # Special case: return dicts that have this field
                filtered = [d for d in self._parent._data if field_name in d]
            else:
                # Apply operator
                if op == "eq":
                    filtered = [d for d in self._parent._data if field_name in d and d[field_name] == value]
                elif op == "gt":
                    filtered = [d for d in self._parent._data if field_name in d and d[field_name] > value]
                elif op == "lt":
                    filtered = [d for d in self._parent._data if field_name in d and d[field_name] < value]
                elif op == "ge":
                    filtered = [d for d in self._parent._data if field_name in d and d[field_name] >= value]
                elif op == "le":
                    filtered = [d for d in self._parent._data if field_name in d and d[field_name] <= value]
                else:
                    raise ValueError(f"Unsupported operator: {op}")
            return FieldCentricAnalyzer(filtered)
        else:
            # In dicts mode, calling not defined (or could be used for something else?)
            raise TypeError(f"'{self.__class__.__name__}' object is not callable")

    def __getitem__(self, index):
        if isinstance(index, int):
            if not self._data:
                return None
            if index < 0 or index >= len(self._data):
                return None
            item = self._data[index]
            if self._mode == "dicts":
                # Return new analyzer with single dict
                return FieldCentricAnalyzer([item])
            else:
                # Return the value
                return item
        else:
            raise TypeError(f"Index must be integer, not {type(index).__name__}")

    def __repr__(self):
        return f"FieldCentricAnalyzer({self._data})"

    def __iter__(self):
        """
        Iterate over the analyzer.

        - If in values mode with a parent: yield (group_value, group_analyzer) pairs
          where group_value is a distinct field value and group_analyzer contains
          all dicts from parent that have that field value.
        - If in dicts mode: yield each dictionary directly.
        - If in values mode without parent: yield each value directly.
        """
        if self._mode == "values" and self._parent is not None:
            # Group by distinct values and yield (value, analyzer) pairs
            # First collect distinct values and their corresponding dicts
            field_name = self._field_name
            groups = {}
            for d in self._parent._data:
                if field_name in d:
                    val = d[field_name]
                    if val not in groups:
                        groups[val] = []
                    groups[val].append(d)

            # Yield (value, analyzer) for each distinct value
            for value, dicts in groups.items():
                yield value, FieldCentricAnalyzer(dicts)
        elif self._mode == "dicts":
            # Yield each dictionary directly
            yield from self._data
        else:
            # values mode without parent (unlikely in normal usage)
            yield from self._data

    @classmethod
    def load(cls, path):
        with open(path, 'r') as f:
            if path.endswith('.jsonl'):
                obj = cls([json.loads(line) for line in f])
                return obj
            else:
                raise ValueError("Unsupported file format")

