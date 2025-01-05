# WorkFlow.py

import os
import json
import re
from typing import Dict, List, TypedDict, Any, Annotated, Callable, Literal
import operator
import inspect
from NodeData import NodeData
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END, START
from llm import get_llm, clip_history

# Tool registry to hold information about tools
tool_registry: Dict[str, Callable] = {}
tool_info_registry: Dict[str, str] = {}

# Decorator to register tools
def tool(func: Callable) -> Callable:
    signature = inspect.signature(func)
    docstring = func.__doc__ or ""
    tool_info = f"{func.__name__}{signature} - {docstring}"
    tool_registry[func.__name__] = func
    tool_info_registry[func.__name__] = tool_info
    return func

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



class PipelineState(TypedDict):
    history: Annotated[str, operator.add]
    task: Annotated[str, operator.add]
    condition: Annotated[bool, lambda x, y: y]

def execute_step(name:str, state: PipelineState, prompt_template: str, llm) -> PipelineState:
    print(f"{name} is working...")
    state["history"] = clip_history(state["history"])
    
    prompt = PromptTemplate.from_template(prompt_template)
    llm_chain = prompt | llm | StrOutputParser()
    inputs = {"history": state["history"]}
    generation = llm_chain.invoke(inputs)
    data = json.loads(generation)
    
    state["history"] += "\n" + json.dumps(data)
    state["history"] = clip_history(state["history"])

    return state

def execute_tool(name: str, state: PipelineState, prompt_template: str, llm) -> PipelineState:

    print(f"{name} is working...")

    state["history"] = clip_history(state["history"])
    
    prompt = PromptTemplate.from_template(prompt_template)
    llm_chain = prompt | llm | StrOutputParser()
    inputs = {"history": state["history"]}
    generation = llm_chain.invoke(inputs)

    # Sanitize the generation output by removing invalid control characters
    sanitized_generation = re.sub(r'[\x00-\x1F\x7F]', '', generation)

    print(sanitized_generation)

    data = json.loads(sanitized_generation)
    
    choice = data
    tool_name = choice["function"]
    args = choice["args"]
    
    if tool_name not in tool_registry:
        raise ValueError(f"Tool {tool_name} not found in registry.")
    
    result = tool_registry[tool_name](*args)

    # Flatten args to a string
    flattened_args = ', '.join(map(str, args))

    print(f"\nExecuted Tool: {tool_name}({flattened_args})  Result is: {result}")


    state["history"] += f"\nExecuted {tool_name}({flattened_args})  Result is: {result}"
    state["history"] = clip_history(state["history"])

    return state

def condition_switch(name:str, state: PipelineState, prompt_template: str, llm) -> PipelineState:
    print(f"{name} is working...")

    state["history"] = clip_history(state["history"])
    
    prompt = PromptTemplate.from_template(prompt_template)
    llm_chain = prompt | llm | StrOutputParser()
    inputs = {"history": state["history"]}
    generation = llm_chain.invoke(inputs)

    data = json.loads(generation)
    
    condition = data["switch"]
    state["condition"] = condition
    
    state["history"] += f"\nCondition is {condition}"
    state["history"] = clip_history(state["history"])

    return state

def info_add(name: str, state: PipelineState, information: str, llm) -> PipelineState:   
    print(f"{name} is adding information...")

    # Append the provided information to the history
    state["history"] += "\n" + information
    state["history"] = clip_history(state["history"])

    return state

def conditional_edge(state: PipelineState) -> Literal["True", "False"]:
    if state["condition"] in ["True", "true", True]:
        return "True"
    else:
        return "False"

def RunWorkFlow(node_map: Dict[str, NodeData], llm):
    # Define the state machine
    workflow = StateGraph(PipelineState)

    # Start node, only one start point
    start_node = find_nodes_by_type(node_map, "START")[0]
    print(f"Start root ID: {start_node.uniq_id}")

    # Step nodes
    step_nodes = find_nodes_by_type(node_map, "STEP")
    for current_node in step_nodes:
        if current_node.tool:
            tool_info = tool_info_registry[current_node.tool]
            prompt_template = f"""
            history: {{history}}
            {current_node.description}
            Available tool: {tool_info}
            Based on Available tool, arguments in the json format:
            "function": "<func_name>", "args": [<arg1>, <arg2>, ...]

            next stage directly parse then run <func_name>(<arg1>,<arg2>, ...) make sure syntax is right json and align function siganture
            """
            workflow.add_node(
                current_node.uniq_id, 
                lambda state, template=prompt_template, llm=llm, name=current_node.name : execute_tool(name, state, template, llm)
            )
        else:
            prompt_template=f"""
            history: {{history}}
            {current_node.description}
            you reply in the json format
            """
            workflow.add_node(
                current_node.uniq_id, 
                lambda state, template=prompt_template, llm=llm, name=current_node.name: execute_step(name, state, template, llm)
            )

    # Add INFO nodes
    info_nodes = find_nodes_by_type(node_map, "INFO")
    for info_node in info_nodes:
        # INFO nodes just append predefined information to the state history
        workflow.add_node(
            info_node.uniq_id, 
            lambda state, template=info_node.description, llm=llm, name=info_node.name: info_add(name, state, template, llm)
        )

    # Edges
    # Find all next nodes from start_node
    next_node_ids = start_node.nexts
    next_nodes = [node_map[next_id] for next_id in next_node_ids]
    
    for next_node in next_nodes:
        print(f"Next node ID: {next_node.uniq_id}, Type: {next_node.type}")
        workflow.add_edge(START, next_node.uniq_id)   

    # Find all next nodes from step_nodes
    for node in step_nodes + info_nodes:
        next_nodes = [node_map[next_id] for next_id in node.nexts]
        
        for next_node in next_nodes:
            print(f"{node.name} {node.uniq_id}'s next node: {next_node.name} {next_node.uniq_id}, Type: {next_node.type}")
            workflow.add_edge(node.uniq_id, next_node.uniq_id)

    # Find all condition nodes
    condition_nodes = find_nodes_by_type(node_map, "CONDITION")
    for condition in condition_nodes:
        condition_template = f"""{condition.description}
        history: {{history}}, decide the condition result in the json format:
        "switch": True/False
        """
        workflow.add_node(
            condition.uniq_id, 
            lambda state, template=condition_template, llm=llm, name=condition.name: condition_switch(name, state, template, llm)
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

def run_workflow_as_server(llm):
    node_map = load_nodes_from_json("graph.json")

    # Register the tool functions dynamically
    for tool in find_nodes_by_type(node_map, "TOOL"):
        tool_code = f"{tool.description}"
        exec(tool_code, globals())

    RunWorkFlow(node_map, llm)
