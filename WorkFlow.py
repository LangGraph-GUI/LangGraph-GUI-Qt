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


    workflow.add_node(START)

    workflow.add_edge('Start', END)






    initial_state = PipelineState(
        history="",
        use_tool=False,
        tool_exec="",
    )

    for state in app.stream(initial_state):
        print(state)



def run_workflow_from_file(filename: str, llm):
    node_map = load_nodes_from_json(filename)
    start_nodes = find_nodes_by_type(node_map, "Start")
    for start_node in start_nodes:
        RunWorkFlow(start_node, node_map, llm)
