import argparse
import sys
import time

from llm import ChatBot, get_llm
from WorkFlow import run_workflow_as_server

def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Run a graph processing task with LLM configuration.")
    
    # Add arguments
    parser.add_argument(
        "--llm", 
        type=str, 
        required=True, 
        help="Specify the LLM model to use (e.g., gpt-4)."
    )
    parser.add_argument(
        "--key", 
        type=str, 
        required=True, 
        help="API key for authentication."
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Access the arguments
    llm_model = args.llm
    api_key = args.key
    
    # Initialize the LLM using the provided model and API key
    llm_instance = get_llm(llm_model, api_key)
    run_workflow_as_server(llm_instance)

if __name__ == "__main__":
    main()
