import re
import yaml
from typing import Dict, Any
from prodxy.operation.attribute_sampler import ProdxyPropertyLibraryConfig, ProdxyPropertyLibrary
from .builder import ProdxyGraph


def transform_mx_config_to_standard(mx_node_configs: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Transform MX config format to standard format by splitting operations/conditions
    based on their suffixes (a), (b), etc.

    Returns:
        Dictionary mapping variant names (a, b, etc.) to standard config dictionaries
    """
    variants = {}

    # First, collect all unique suffixes from operations and conditions
    all_suffixes = set()
    has_default_operations = False
    has_default_conditions = False

    for node in mx_node_configs:
        for key in node.keys():
            if key == 'operations':
                has_default_operations = True
            elif key == 'conditions':
                has_default_conditions = True
            elif key.startswith('operations(') or key.startswith('conditions('):
                # Extract suffix from parentheses
                match = re.match(r'(?:operations|conditions)\((.+?)\)', key)
                if match:
                    suffix = match.group(1)
                    all_suffixes.add(suffix)

    # Create a config for each suffix
    for suffix in sorted(all_suffixes):
        standard_nodes = []
        for node in mx_node_configs:
            standard_node = {'name': node['name']}
            has_suffix_content = False

            # Add operations for this suffix
            operations_key = f'operations({suffix})'
            if operations_key in node:
                standard_node['operations'] = node[operations_key]
                has_suffix_content = True

            # Add conditions for this suffix
            conditions_key = f'conditions({suffix})'
            if conditions_key in node:
                standard_node['conditions'] = node[conditions_key]
                has_suffix_content = True

            # Only include nodes that have content for this suffix
            if has_suffix_content:
                standard_nodes.append(standard_node)

        variants[suffix] = standard_nodes

    # Create _default variant if there are base operations or conditions
    if has_default_operations or has_default_conditions:
        default_nodes = []
        for node in mx_node_configs:
            standard_node = {'name': node['name']}
            has_base_content = False

            # Add base operations
            if 'operations' in node:
                standard_node['operations'] = node['operations']
                has_base_content = True

            # Add base conditions
            if 'conditions' in node:
                standard_node['conditions'] = node['conditions']
                has_base_content = True

            # Only include nodes that have base operations or conditions
            if has_base_content:
                default_nodes.append(standard_node)

        variants['_default'] = default_nodes

    # If no variants found at all, treat as standard format
    if not variants:
        return {'_default': mx_node_configs}

    return variants



class ProdxyMxBuilder:
    def __init__(
        self,
        mx_node_configs: dict,
        properties: dict = None,
        constrains: dict = None,
        start_node_placeholder: str = None,
        end_node_placeholder: str = None
    ):

        self.prodxy_graphs = []
        variants = transform_mx_config_to_standard(mx_node_configs)
        self.variant_name_to_index_map = {}
        variant_index = 0
        for variant_name, variant_conf in variants.items():
            current_prodxy_graph_config = {
                "node_configs": variant_conf,
                "name": variant_name,
            }
            if start_node_placeholder:
                current_prodxy_graph_config['start_node_placeholder'] = start_node_placeholder
            if end_node_placeholder:
                current_prodxy_graph_config['end_node_placeholder'] = end_node_placeholder
            
            self.prodxy_graphs.append(ProdxyGraph.from_dict(current_prodxy_graph_config))
            self.variant_name_to_index_map[variant_name] = variant_index
            variant_index += 1
        
        current_prodxy_property_library_config = {}
        if properties is not None:
            current_prodxy_property_library_config['properties'] = properties
        if constrains is not None:
            current_prodxy_property_library_config['constrains'] = constrains
        self.property_library = ProdxyPropertyLibrary.load_from_dict(current_prodxy_property_library_config)

        # load the property library to graphs' data
        for pg in self.prodxy_graphs:
            pg.pre_loaded_data.update({"_prodxy_property_library": self.property_library})
    
    def __call__(self, variant_name):
        variant_index = self.variant_name_to_index_map.get(variant_name)
        if variant_index is not None and variant_index < len(self.prodxy_graphs):
            return self.prodxy_graphs[variant_index].__call__
        

    @classmethod
    def load_from_dict(cls, data):
        return cls(
            mx_node_configs=data['mx_node_configs'],
            properties=data.get('properties'),
            constrains=data.get('constrains'),
            start_node_placeholder=data.get('start_node_placeholder'),
            end_node_placeholder=data.get('end_node_placeholder'),
        )

    @classmethod
    def load_from_yaml(cls, yaml_path: str):
        """Load configuration from YAML file"""
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
        return cls.load_from_dict(data)
    


