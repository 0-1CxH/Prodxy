import datetime
import random
import yaml
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from langgraph.graph import StateGraph, START, END
from prodxy.operation import OperationMap
from .state import JsonPathDict



@dataclass
class ProdxyGlobalState:
    data: Dict
    condition_signal: Optional[str] = None
    prodxy_trace: Optional[List[Dict]] = None

    def __post_init__(self):
        if self.prodxy_trace is None:
            self.prodxy_trace = []

@dataclass
class ProdxyOperationConfig:
    main_op_name: str
    condition_op_name: str
    read_paths: Dict[str, str]
    write_path: str

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            main_op_name=data["main_op_name"],
            condition_op_name=data["condition_op_name"],
            read_paths=data["read_paths"],
            write_path=data["write_path"],
        )


def get_random_id():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(0, 1000))


@dataclass
class ProdxyNodeConfig:
    operations: List[ProdxyOperationConfig]
    name: str = None
    conditions: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.name is None:
            self.name = get_random_id()
        if self.conditions is None:
            self.conditions = {}
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            operations=[ProdxyOperationConfig.from_dict(operation_config) for operation_config in data["operations"]],
            name=data.get('name'),
            conditions=data.get("conditions"),
        )

@dataclass
class ProdxyGraphConfig:
    node_configs: List[ProdxyNodeConfig]
    name: str = None
    start_node_placeholder: str = None
    end_node_placeholder: str = None

    def __post_init__(self):
        if self.name is None:
            self.name = get_random_id()
        if self.start_node_placeholder is None:
            self.start_node_placeholder = '_start'
        if self.end_node_placeholder is None:
            self.end_node_placeholder = '_end'


    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            node_configs=[ProdxyNodeConfig.from_dict(node_config) for node_config in data["node_configs"]],
            name=data.get('name'),
            start_node_placeholder=data.get("start_node_placeholder"),
            end_node_placeholder=data.get("end_node_placeholder"),
        )


class ProdxyNode:
    def __init__(self, config: ProdxyNodeConfig):
        self.config = config

    def _execute_operation(self, operation_config: ProdxyOperationConfig, global_state: ProdxyGlobalState):
        '''Execute a single operation and return updated global state and condition signal'''
        if operation_config.main_op_name not in OperationMap:
            raise ValueError(f"operation {operation_config.main_op_name} not registered")

        if operation_config.condition_op_name not in OperationMap:
            raise ValueError(f"operation {operation_config.condition_op_name} not registered")

        if operation_config.main_op_name == "property:sample":
            operation_func = global_state.data['_prodxy_property_library'].sample
        else:    
            operation_func = OperationMap[operation_config.main_op_name]
        condition_func = OperationMap[operation_config.condition_op_name]

        # Prepare real arguments by resolving paths
        global_state_data = JsonPathDict(global_state.data)
        arg_values = {}

        for argkey, argpath in operation_config.read_paths.items():
            if isinstance(argpath, str):
                if argpath.startswith('@'): # literal string
                    argliteral =  argpath[1:]
                    try:
                        arg_values[argkey] = eval(argliteral)
                    except:
                        arg_values[argkey] = argliteral
                elif argpath.startswith('$'): # json path
                    arg_values[argkey] = global_state_data[argpath]
                else:
                    arg_values[argkey] = argpath
            else:
                arg_values[argkey] = argpath
            
        
        # Execute operation
        retval = operation_func(**arg_values)
        
        # Execute condition function
        condition_signal = condition_func(retval)
        
        # Update global state
        global_state_data[operation_config.write_path] = retval

        # convert back to dict
        global_state.data = global_state_data.d

        op_trace = {
            "op": operation_config.main_op_name,
            "arg_values": arg_values,
            "retval": retval,
            "condition_signal": condition_signal
        }

        return condition_signal, op_trace

    def __call__(self, global_state: ProdxyGlobalState):
        '''
        global state in, global state out
        '''
        node_trace = {
            "node": self.config.name,
            "operations": [],
        }
        for operation_config in self.config.operations:
            condition_signal, op_trace = self._execute_operation(operation_config, global_state)
            node_trace["operations"].append(op_trace)
            if condition_signal is not None:
                global_state.condition_signal = condition_signal
        global_state.prodxy_trace.append(node_trace)

        return global_state

class ProdxyGraph:

    def __init__(self, graph_config: ProdxyGraphConfig):
        self.graph_config = graph_config
        self.name = graph_config.name
        self.node_configs = graph_config.node_configs
        self.graph = StateGraph(ProdxyGlobalState)

        all_nodes = []
        nodes_without_source = []
        nodes_without_target = []

        # add nodes to the graph
        for node_config in graph_config.node_configs:
            self.graph.add_node(node_config.name, ProdxyNode(node_config))
            all_nodes.append(node_config.name)
            nodes_without_source.append(node_config.name)
            nodes_without_target.append(node_config.name)
        
        # add edges to the graph and remove nodes from nodes_without_x
        for node_config in graph_config.node_configs:
            for condition, target_node_name in node_config.conditions.items():
                if target_node_name in [graph_config.start_node_placeholder, graph_config.end_node_placeholder]:
                    continue
                if target_node_name not in all_nodes:
                    raise ValueError(f"node {target_node_name} not found")
                if target_node_name in nodes_without_source:
                    nodes_without_source.remove(target_node_name)
                if node_config.name in nodes_without_target:
                    nodes_without_target.remove(node_config.name)
            if node_config.conditions:
                # replace '_start' and '_end' with real START and END
                node_config.conditions = {
                    condition: START if target_node_name == graph_config.start_node_placeholder else END if target_node_name == graph_config.end_node_placeholder else target_node_name
                    for condition, target_node_name in node_config.conditions.items()
                }
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
        self.pre_loaded_data = {}
    
    async def __call__(self, input_data):
        if input_data is None:
            input_data = {}
        input_data.update(self.pre_loaded_data)
        global_state = ProdxyGlobalState(
            data=input_data
        )
        await self.compiled_graph.ainvoke(global_state)
        return global_state
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            graph_config=ProdxyGraphConfig.from_dict(data),
        )
    
    @classmethod
    def from_yaml(cls, yaml_path: str):
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)
