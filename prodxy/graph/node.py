# class ProdxyOperation:
#     def __init__(self, name: str, args: dict):
#         self.name = name
#         if name not in OperationMap:
#             raise ValueError(f"operation {name} not registered")
#         self.func = OperationMap.get(name)
#         self.args = args
#         self.local_states = {'name': name, 'args': args}
    
#     def __call__(self, global_states: JsonPathDict):
#         kwargs = {}
#         for argkey in args:
#             argpath = args[argkey]
#             kwargs[argkey] = global_states[argpath]
#         self.local_states['real_args'] = kwargs
#         ret = self.func(**kwargs)
#         self.local_states['retval'] = ret
#         return ret


# class ProdxyNode:
#     def __init__(self, name, operations, conditions):
#         self.name = name
#         self.operations = operations
#         self.conditions = conditions
#         self.local_states = {}
    
#     def __call__(self, global_states):
#         condition_signal = None
#         for _op in self.operations:
#             op_ret = _op(global_states)
#             if op_ret.get('condition_signal'):
#                 condition_signal = op_ret['condition_signal']
#             if op_ret.get('prodxy_trace'):
#                 global_states
            


            
