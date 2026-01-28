import json

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

