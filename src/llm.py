# llm.py

from langgraph.graph import Graph

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
import json

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_community.chat_models import ChatOpenAI

import os

def get_llm(llm_model, open_ai_key):
    if "gpt" in llm_model.lower():  # If the llm contains 'gpt', use ChatOpenAI
        os.environ["OPENAI_API_KEY"] = open_ai_key
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini").bind(response_format={"type": "json_object"})
        print("Using gpt-4o-mini")
    
    if "gemma2" in llm_model.lower():
        print("Initializing ChatOllama with model: gemma2")
        llm = ChatOllama(
            model="gemma2",
            base_url='http://ollama:13666',
            format="json", 
            temperature=0)

    # Initialize the ChatOllama model with desired parameters
    return llm



# Clip the history to the last 16000 characters
def clip_history(history: str, max_chars: int = 32000) -> str:
    if len(history) > max_chars:
        return history[-max_chars:]
    return history

def ChatBot(llm, question):
    # Define the prompt template
    template = """
        {question}
        you reply json in {{ reply:"<content>" }}
    """

    prompt = PromptTemplate.from_template(clip_history(template))

    # Format the prompt with the input variable
    formatted_prompt = prompt.format(question=question)

    llm_chain = prompt | llm | StrOutputParser()
    generation = llm_chain.invoke(formatted_prompt)
    
    data = json.loads(generation)
    reply = data.get("reply", "")

    return reply