import os
import json
import configparser
from typing import Dict, List, TypedDict
from NodeData import NodeData
from langchain_community.llms import Ollama
import networkx as nx

from langgraph.graph import StateGraph, END, START


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


    class PipelineState(TypedDict):
        history: str
        task: str

    # Define the state machine
    workflow = StateGraph(PipelineState)
    app = workflow.compile()


    # from root find step
    sub_node_map = {next_id: node_map[next_id] for next_id in node.nexts}
    # Use BFS to collect all task nodes
    task_nodes = []
    queue = find_nodes_by_type(sub_node_map, "STEP")
    
    while queue:
        current_node = queue.pop(0)
        if current_node not in task_nodes:
            print(f"Processing task_node ID: {current_node.uniq_id}")
            task_nodes.append(current_node)
            next_sub_node_map = {next_id: node_map[next_id] for next_id in current_node.nexts}
            queue.extend(find_nodes_by_type(next_sub_node_map, "STEP"))




    initial_state = PipelineState(
        history="",
        use_tool=False,
        tool_exec="",
    )

    for state in app.stream(initial_state):
        print(state)



def run_workflow_from_file(filename: str, llm):
    node_map = load_nodes_from_json(filename)
    start_nodes = find_nodes_by_type(node_map, "START")
    for start_node in start_nodes:
        RunWorkFlow(start_node, node_map, llm)
