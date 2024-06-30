import os
import json
import configparser
from typing import Dict, List
from NodeData import NodeData
from langchain_community.llms import Ollama
from langchain.chat_models import ChatOpenAI
import networkx as nx

def load_nodes_from_json(filename: str) -> Dict[str, NodeData]:
    with open(filename, 'r') as file:
        data = json.load(file)
        node_map = {}
        for node_data in data["nodes"]:
            node = NodeData.from_dict(node_data)
            node_map[node.uniq_id] = node
        return node_map

def find_nodes_by_type(node_map: Dict[str, NodeData], node_type: str) -> List[NodeData]:
    return [node for node in node_map.values() if node.type == node_type]

def find_node_by_type(node_map: Dict[str, NodeData], node_type: str) -> NodeData:
    for node in node_map.values():
        if node.type == node_type:
            return node
    return None

def RunWorkFlow(node: NodeData, node_map: Dict[str, NodeData], llm):
    print(f"Start root ID: {node.uniq_id}")


def run_workflow_from_file(filename: str, llm):
    node_map = load_nodes_from_json(filename)
    start_nodes = find_nodes_by_type(node_map, "Start")
    for start_node in start_nodes:
        RunWorkFlow(start_node, node_map, llm)
