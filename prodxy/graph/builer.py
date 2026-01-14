import time
from typing import List, Dict
from dataclasses import dataclass
from .analyzer import JsonPathDict
from prodxy.operation import OperationMap
from langgraph.graph import StateGraph, START, END


@dataclass
class ProdxyGlobalState:
    data: Dict
    condition_signal: str
    prodxy_trace: List[Dict]

@dataclass
class ProdxyOperationConfig:
    main_op_name: str
    condition_op_name: str
    read_paths: Dict[str, str]
    write_path: str

@dataclass
class ProdxyNodeConfig:
    name: str
    operations: List[ProdxyOperationConfig]
    conditions: Dict[str, str] = None

    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}

class ProdxyNode:
    def __init__(self, config: ProdxyNodeConfig):
        self.config = config

    def _execute_operation(self, operation_config: ProdxyOperationConfig, global_state: ProdxyGlobalState):
        '''Execute a single operation and return updated global state and condition signal'''
        if operation_config.main_op_name not in OperationMap:
            raise ValueError(f"operation {operation_config.main_op_name} not registered")

        if operation_config.condition_op_name not in OperationMap:
            raise ValueError(f"operation {operation_config.condition_op_name} not registered")

        operation_func = OperationMap[operation_config.main_op_name]
        condition_func = OperationMap[operation_config.condition_op_name]

        
        trace = []
        trace.append({"time": time.time(), "status": "init", "operation": operation_config.main_op_name, "args": operation_config})

        # Prepare real arguments by resolving paths
        global_state_data = JsonPathDict(global_state.data)
        real_args = {}

        for argkey, argpath in operation_config.read_paths.items():
            real_args[argkey] = global_state_data[argpath]
            trace.append({"time": time.time(), "status": "arg", "argkey": argkey, "argpath": argpath, "argvalue": global_state_data[argpath]})

        trace.append({"time": time.time(), "status": "func"})

        # Execute operation
        retval = operation_func(**real_args)

        trace.append({"time": time.time(), "status": "return", "ret": retval})

        # Execute condition function
        condition_signal = condition_func(retval)
        trace.append({"time": time.time(), "status": "condition", "condition_signal": condition_signal})

        # Update global state
        global_state_data[operation_config.write_path] = retval

        # convert back to dict
        global_state.data = global_state_data.d

        global_state.prodxy_trace.append({
            "node": self.config.name,
            "trace": trace,
        })

        return condition_signal

    def __call__(self, global_state: ProdxyGlobalState):
        '''
        global state in, global state out
        '''
        for operation_config in self.config.operations:
            condition_signal = self._execute_operation(operation_config, global_state)
            if condition_signal is not None:
                global_state.condition_signal = condition_signal

        return global_state

class ProdxyGraph:

    def __init__(self, node_configs: List[ProdxyNodeConfig]):
        self.graph = StateGraph(ProdxyGlobalState)
        self.node_configs = node_configs

        all_nodes = []
        nodes_without_source = []
        nodes_without_target = []

        # add nodes to the graph
        for node_config in self.node_configs:
            self.graph.add_node(node_config.name, ProdxyNode(node_config))
            all_nodes.append(node_config.name)
            nodes_without_source.append(node_config.name)
            nodes_without_target.append(node_config.name)
        
        # add edges to the graph and remove nodes from nodes_without_x
        for node_config in self.node_configs:
            for condition, target_node_name in node_config.conditions.items():
                if target_node_name not in all_nodes:
                    raise ValueError(f"node {target_node_name} not found")
                if target_node_name in nodes_without_source:
                    nodes_without_source.remove(target_node_name)
                if node_config.name in nodes_without_target:
                    nodes_without_target.remove(node_config.name)
            if node_config.conditions:
                self.graph.add_conditional_edges(
                        node_config.name,
                        lambda global_state: global_state.condition_signal,
                        node_config.conditions,
                    )

        # add start and end nodes
        for node in nodes_without_source:
            self.graph.add_edge(START, node)
        for node in nodes_without_target:
            self.graph.add_edge(node, END)
        

        self.compiled_graph = self.graph.compile()
    
    def __call__(self, input_data):
        global_state = ProdxyGlobalState(
            data=input_data,
            condition_signal=None,
            prodxy_trace=[],
        )
        self.compiled_graph.invoke(global_state)
        return global_state


        

