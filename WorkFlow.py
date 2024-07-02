# WorkFlow.py

import os
import json
from typing import Dict, List, TypedDict, Any, Annotated, Callable, Literal
import operator
import inspect
from NodeData import NodeData
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END, START

# Tool registry to hold information about tools
tool_registry: Dict[str, Callable] = {}
tool_info_registry: List[Dict[str, Any]] = []

# Decorator to register tools
def tool(func: Callable) -> Callable:
    signature = inspect.signature(func)
    docstring = func.__doc__ or ""
    params = [
        {"name": param.name, "type": param.annotation}
        for param in signature.parameters.values()
    ]
    tool_info = {
        "name": func.__name__,
        "description": docstring,
        "parameters": params
    }
    tool_registry[func.__name__] = func
    tool_info_registry.append(tool_info)
    return func

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
    history: Annotated[str, operator.add]
    task: Annotated[str, operator.add]
    condition: Annotated[bool, ""]

def execute_task(state: PipelineState, prompt_template: str) -> PipelineState:
    state["history"] = clip_history(state["history"])
    
    prompt = PromptTemplate.from_template(prompt_template)
    llm_chain = prompt | llm | StrOutputParser()
    inputs = {"history": state["history"]}
    generation = llm_chain.invoke(inputs)
    data = json.loads(generation)
    
    print(data)

    state["history"] += "\n" + json.dumps(data)
    state["history"] = clip_history(state["history"])

    return state

def execute_tool(state: PipelineState, prompt_template: str) -> PipelineState:
    state["history"] = clip_history(state["history"])
    
    prompt = PromptTemplate.from_template(prompt_template)
    llm_chain = prompt | llm | StrOutputParser()
    inputs = {"history": state["history"]}
    generation = llm_chain.invoke(inputs)

    data = json.loads(generation)
    
    print(data)

    choice = data
    tool_name = choice["function"]
    args = choice["args"]
    
    if tool_name not in tool_registry:
        raise ValueError(f"Tool {tool_name} not found in registry.")
    
    result = tool_registry[tool_name](*args)
    state["history"] += f"\nExecuted {tool_name} with result: {result}"
    state["history"] = clip_history(state["history"])

    return state

def condition_switch(state: PipelineState, prompt_template: str) -> PipelineState:
    state["history"] = clip_history(state["history"])
    
    prompt = PromptTemplate.from_template(prompt_template)
    llm_chain = prompt | llm | StrOutputParser()
    inputs = {"history": state["history"]}
    generation = llm_chain.invoke(inputs)

    data = json.loads(generation)
    
    print(data)

    condition = data["condition"]
    state["condition"] = condition
    
    state["history"] += f"\nResult is {condition}"
    state["history"] = clip_history(state["history"])

    return state

def conditional_edge(state: PipelineState) -> Literal["True", "False"]:
    return "True" if state["condition"] else "False"

def RunWorkFlow(node_map: Dict[str, NodeData], llm):
    # Define the state machine
    workflow = StateGraph(PipelineState)

    # Start node, only one start point
    start_node = find_nodes_by_type(node_map, "START")[0]
    print(f"Start root ID: {start_node.uniq_id}")

    # Tool nodes for lookup
    tool_nodes = find_nodes_by_type(node_map, "TOOL")
    tool_map = {tool_node.name: tool_node.description for tool_node in tool_nodes}

    # Step nodes
    step_nodes = find_nodes_by_type(node_map, "STEP")
    for current_node in step_nodes:
        if current_node.tool:
            tool_description = tool_map[current_node.tool]
            prompt_template = f"""{current_node.description}
            Available tool: {tool_description}
            Based on the history, choose the appropriate tool and arguments in the json format:
            "function": "<function>", "args": [<arg1>, <arg2>, ...]

            next stage directly parse then run <function>(<arg1>,<arg2>, ...) make sure syntax can run
            """
            workflow.add_node(
                current_node.uniq_id, 
                lambda state, template=prompt_template: execute_tool(state, template)
            )
        else:
            workflow.add_node(
                current_node.uniq_id, 
                lambda state, template=current_node.description: execute_task(state, template)
            )

    # Edges
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

    # Find all condition nodes
    condition_nodes = find_nodes_by_type(node_map, "CONDITION")
    for condition in condition_nodes:
        condition_template = f"""{condition.description}
        Based on the history, decide the condition result in the json format:
        "condition": True/False
        """
        workflow.add_node(
            condition.uniq_id, 
            lambda state, template=condition_template: condition_switch(state, template)
        )

        print(f"{condition.name} {condition.uniq_id}'s condition")
        print(f"true will go {condition.true_next}")
        print(f"false will go {condition.false_next}")
        workflow.add_conditional_edges(
            condition.uniq_id,
            conditional_edge,
            {
                "True": condition.true_next if condition.true_next else END,
                "False": condition.false_next if condition.false_next else END
            }
        )

    initial_state = PipelineState(
        history="",
        task="",
        condition=False
    )

    app = workflow.compile()
    for state in app.stream(initial_state):
        print(state)

def run_workflow_from_file(filename: str, llm):
    node_map = load_nodes_from_json(filename)

    # Tool nodes for lookup
    tool_nodes = find_nodes_by_type(node_map, "TOOL")
    tool_map = {tool_node.name: tool_node.description for tool_node in tool_nodes}

    for tool in tool_nodes:
        tool_code = f"{tool.description}"
        # Register the tool function dynamically
        exec(tool_code, globals())

    RunWorkFlow(node_map, llm)

