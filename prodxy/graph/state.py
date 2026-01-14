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
            # use original update can only 'update' on existing value
            if JsonPathAnalyzer.get(d, jsonpath_str) is not None:
                jsonpath_parser.update(d, value)
            # need to use other way to write new value
            else:
                # Create new value when the JSONPath doesn't exist
                # This requires manual path traversal and creation
                parts = jsonpath_str.split('.')
                current_obj = d

                # Traverse through the path, creating objects as needed
                for i, part in enumerate(parts[:-1]):
                    if i == 0 and part == '$':
                        continue
                    # Handle array indices like [0], [1], etc.
                    if part.endswith(']'):
                        # Extract the array name and index
                        array_part = part.split('[')[0]
                        index = int(part.split('[')[1].rstrip(']'))

                        # Ensure the array exists
                        if array_part not in current_obj:
                            current_obj[array_part] = []
                        elif not isinstance(current_obj[array_part], list):
                            # Convert to list if it's not already
                            current_obj[array_part] = [current_obj[array_part]]

                        # Ensure the array is long enough
                        while len(current_obj[array_part]) <= index:
                            current_obj[array_part].append({})

                        current_obj = current_obj[array_part][index]
                    else:
                        # Handle regular object keys
                        if part not in current_obj:
                            current_obj[part] = {}
                        current_obj = current_obj[part]

                # Set the final value
                last_part = parts[-1]
                if last_part.endswith(']'):
                    # Handle array assignment
                    array_part = last_part.split('[')[0]
                    index = int(last_part.split('[')[1].rstrip(']'))

                    if array_part not in current_obj:
                        current_obj[array_part] = []
                    elif not isinstance(current_obj[array_part], list):
                        current_obj[array_part] = [current_obj[array_part]]

                    # Ensure the array is long enough
                    while len(current_obj[array_part]) <= index:
                        current_obj[array_part].append(None)

                    current_obj[array_part][index] = value
                else:
                    # Regular key assignment
                    current_obj[last_part] = value

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
    def __init__(self, d: dict = None):
        if d is None:
            d = {}
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

