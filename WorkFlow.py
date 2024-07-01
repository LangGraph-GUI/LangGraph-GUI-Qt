import os
import json
from typing import Dict, List, TypedDict, Any
import operator
from NodeData import NodeData
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END, START

# Load local language model
local_llm = "mistral"
llm = ChatOllama(model=local_llm, format="json", temperature=0)

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

# Clip the history to the last 8000 characters
def clip_history(history: str, max_chars: int = 8000) -> str:
    if len(history) > max_chars:
        return history[-max_chars:]
    return history

class PipelineState(TypedDict):
    history: str
    roll_number: int

def execute_task(state: PipelineState, prompt_template: str) -> PipelineState:
    state["history"] = clip_history(state["history"])
    
    prompt = PromptTemplate.from_template(prompt_template)
    llm_chain = prompt | llm | StrOutputParser()
    inputs = {"history": state["history"], "roll_number": -1}
    generation = llm_chain.invoke(inputs)
    data = json.loads(generation)
    
    print(data)

    state["history"] += "\n" + json.dumps(data)
    state["history"] = clip_history(state["history"])

    return state

def RunWorkFlow(node_map: Dict[str, NodeData], llm):
    # Define the state machine
    workflow = StateGraph(PipelineState)

    # Start node, only one start point
    start_node = find_nodes_by_type(node_map, "START")[0]
    print(f"Start root ID: {start_node.uniq_id}")

    # Step nodes
    step_nodes = find_nodes_by_type(node_map, "STEP")
    for current_node in step_nodes:
        workflow.add_node(
            current_node.uniq_id, 
            lambda state, template=current_node.description: execute_task(state, template)
        )

    # edges
    # Find all next nodes from start_node
    next_node_ids = start_node.nexts
    next_nodes = [node_map[next_id] for next_id in next_node_ids]
    
    for next_node in next_nodes:
        print(f"Next node ID: {next_node.uniq_id}, Type: {next_node.type}")
        workflow.add_edge(START, next_node.uniq_id)   

    # Find all next nodes from step_nodes
    for node in step_nodes:
        next_nodes = [node_map[next_id] for next_id in node.nexts]
        
        for next_node in next_nodes:
            print(f"{node.name} {node.uniq_id}'s next node: {next_node.name} {next_node.uniq_id}, Type: {next_node.type}")
            workflow.add_edge(node.uniq_id, next_node.uniq_id)   

    initial_state = PipelineState(
        history="",
        roll_number = -1
    )

    app = workflow.compile()
    for state in app.stream(initial_state):
        print(state)

def run_workflow_from_file(filename: str, llm):
    node_map = load_nodes_from_json(filename)
    RunWorkFlow(node_map, llm)

