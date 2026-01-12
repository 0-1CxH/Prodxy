class JudgePrimitives:
    @staticmethod
    def equal(target, source, depth=0):
        # Helper to check if a value is a non-container type
        def is_non_container(obj):
            return not (isinstance(obj, (list, set, tuple, dict)))

        # Helper to check if a value is a kv-container type (dictionary)
        def is_kv_container(obj):
            return isinstance(obj, dict)

        # Helper to check if a value is a non-kv container type (list, set, tuple)
        def is_non_kv_container(obj):
            return isinstance(obj, (list, set, tuple))

        # Case 1: target is non-container type
        if is_non_container(target):
            # source should also be non-container type
            if not is_non_container(source):
                return False
            # Direct comparison with type conversion attempt
            if target == source:
                return True
            # Try string conversion
            try:
                if str(target) == str(source):
                    return True
            except:
                pass
            return False

        # Case 2: target is non-kv container type
        elif is_non_kv_container(target):
            # source should also be non-kv container type
            if not is_non_kv_container(source):
                return False

            # For lists: order matters at top level (depth=0), unordered at nested levels (depth>0)
            # For tuples: always ordered (based on test expectation)
            # For sets: always unordered
            if isinstance(target, list) and isinstance(source, list):
                # List-list comparison
                if depth == 0:
                    # Top-level: ordered comparison
                    if len(target) != len(source):
                        return False
                    for t_elem, s_elem in zip(target, source):
                        if not JudgePrimitives.equal(t_elem, s_elem, depth+1):
                            return False
                    return True
                else:
                    # Nested: unordered comparison
                    target_list = list(target)
                    source_list = list(source)
                    if len(target_list) != len(source_list):
                        return False
                    matched = [False] * len(source_list)
                    for t_elem in target_list:
                        found = False
                        for i, s_elem in enumerate(source_list):
                            if not matched[i] and JudgePrimitives.equal(t_elem, s_elem, depth+1):
                                matched[i] = True
                                found = True
                                break
                        if not found:
                            return False
                    return True
            elif isinstance(target, tuple) and isinstance(source, tuple):
                # Tuple-tuple: ordered comparison (based on test assertion)
                if len(target) != len(source):
                    return False
                for t_elem, s_elem in zip(target, source):
                    if not JudgePrimitives.equal(t_elem, s_elem, depth+1):
                        return False
                return True
            else:
                # Mixed types or involving sets: unordered comparison
                target_list = list(target)
                source_list = list(source)
                if len(target_list) != len(source_list):
                    return False
                matched = [False] * len(source_list)
                for t_elem in target_list:
                    found = False
                    for i, s_elem in enumerate(source_list):
                        if not matched[i] and JudgePrimitives.equal(t_elem, s_elem, depth+1):
                            matched[i] = True
                            found = True
                            break
                    if not found:
                        return False
                return True

        # Case 3: target is kv-container type (dict)
        elif is_kv_container(target):
            # source should also be kv-container type
            if not is_kv_container(source):
                return False

            # Check keys first
            if set(target.keys()) != set(source.keys()):
                return False

            # Compare values recursively for each key
            for key in target:
                if not JudgePrimitives.equal(target[key], source[key], depth+1):
                    return False
            return True

        # Any other type
        return False
    

    @staticmethod
    def include(target, source, recursive=False):
        # target should be iterable (string, dict, list, set, tuple, ...)
        # if recursive is true, use 'include' on non-top layer compare instead of 'equal'
        # if target is string, source can be string, number or any type that can be converted to string, compare in string foramt
        # elif target is not kv-container type (list, set, tuple, ...), source can be:
        #       (1) non-container type: check if source is in target
        #       (2) non-kv-container type: loop inspect elems in source
        # elif target is kv-container type (dict, ...), source can be:
        #       (1) non-container type or  non-kv-container type: check if source is in target's ks or vs
        #       (2) kv-container type: loop inspect k-v pair in source, inspect if all kvs are in target

        # Helper functions from equal method
        def is_non_container(obj):
            return not (isinstance(obj, (list, set, tuple, dict)))

        def is_kv_container(obj):
            return isinstance(obj, dict)

        def is_non_kv_container(obj):
            return isinstance(obj, (list, set, tuple))

        # Helper to check if an object is iterable (but not string)
        def is_iterable_non_string(obj):
            return hasattr(obj, '__iter__') and not isinstance(obj, str)

        # Choose comparison function based on recursive flag
        def compare_func(t, s):
            if recursive:
                # For non-container types, use equal; for container types, use include
                if is_non_container(t) and is_non_container(s):
                    return JudgePrimitives.equal(t, s)
                else:
                    return JudgePrimitives.include(t, s, recursive=True)
            else:
                return JudgePrimitives.equal(t, s)

        # Case 1: target is string
        if isinstance(target, str):
            # Convert source to string for comparison
            try:
                source_str = str(source)
            except:
                return False

            # Check if source string is in target string
            return source_str in target

        # Case 2: target is non-kv container type (list, set, tuple)
        elif is_non_kv_container(target):
            # Subcase 2.1: source is non-container type
            if is_non_container(source):
                # Check if source is in target
                return source in target

            # Subcase 2.2: source is non-kv container type
            elif is_non_kv_container(source):
                # For sets, convert to lists for element-by-element comparison
                if isinstance(target, set):
                    target_list = list(target)
                else:
                    target_list = list(target)

                if isinstance(source, set):
                    source_list = list(source)
                else:
                    source_list = list(source)

                # Check if every element in source is included in target
                for s_elem in source_list:
                    found = False
                    for t_elem in target_list:
                        if compare_func(t_elem, s_elem):
                            found = True
                            break
                    if not found:
                        return False
                return True

            # Subcase 2.3: source is kv-container type or other type
            else:
                # For non-recursive include, kv-container source cannot be included in non-kv-container target
                if not recursive and is_kv_container(source):
                    return False
                # Check if any element in target matches source using compare_func
                for t_elem in target:
                    if compare_func(t_elem, source):
                        return True
                return False

        # Case 3: target is kv-container type (dict)
        elif is_kv_container(target):
            # Subcase 3.1: source is non-container type or non-kv container type
            if is_non_container(source) or is_non_kv_container(source):
                # If source is non-container type (single element)
                if is_non_container(source):
                    # Check if source is in target's keys or values
                    for key, value in target.items():
                        if compare_func(key, source) or compare_func(value, source):
                            return True
                    return False
                else:
                    # source is non-kv container type (list, set, tuple)
                    # Check if all elements in source are keys OR all are values
                    # Cannot mix keys and values
                    source_list = list(source)
                    if len(source_list) == 0:
                        return True  # Empty container is always included

                    # Check if all elements are keys
                    all_keys = True
                    for s_elem in source_list:
                        found = False
                        for key in target.keys():
                            if compare_func(key, s_elem):
                                found = True
                                break
                        if not found:
                            all_keys = False
                            break

                    # Check if all elements are values
                    all_values = True
                    for s_elem in source_list:
                        found = False
                        for value in target.values():
                            if compare_func(value, s_elem):
                                found = True
                                break
                        if not found:
                            all_values = False
                            break

                    # Return True if all elements are keys OR all are values
                    return all_keys or all_values

            # Subcase 3.2: source is kv-container type
            elif is_kv_container(source):
                # Check if all key-value pairs in source are included in target
                for s_key, s_value in source.items():
                    found = False
                    for t_key, t_value in target.items():
                        if compare_func(t_key, s_key) and compare_func(t_value, s_value):
                            found = True
                            break
                    if not found:
                        return False
                return True

            else:
                return False

        # Case 4: target is other iterable type (custom iterable)
        elif is_iterable_non_string(target):
            # Similar to non-kv container case but for custom iterables
            if is_non_container(source):
                # Check if source is in target
                for item in target:
                    if compare_func(item, source):
                        return True
                return False

            elif is_iterable_non_string(source):
                # Check if every element in source is included in target
                for s_elem in source:
                    found = False
                    for t_elem in target:
                        if compare_func(t_elem, s_elem):
                            found = True
                            break
                    if not found:
                        return False
                return True

            else:
                return False

        # Target is not iterable (invalid according to spec)
        else:
            return False