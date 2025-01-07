# llm.py

import os
import json

from pydantic import BaseModel, Field

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_llm(llm_model, api_key):

    if "gpt" in llm_model.lower():  # If the llm contains 'gpt', use ChatOpenAI
        from langchain_community.chat_models import ChatOpenAI
        os.environ["OPENAI_API_KEY"] = api_key
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini").bind(response_format={"type": "json_object"})
        print("Using gpt-4o-mini")

        return llm


    if "gemma2" in llm_model.lower():
        from langchain_ollama import ChatOllama
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")  # Default value if envvar is not set
        llm = ChatOllama(
            model="gemma2",
            base_url=ollama_base_url,
            format="json",
            temperature=0)

        print("Using gemma2")
        return llm

    
    # cannot work now, need langchain fix error
    if "gemini" in llm_model.lower():
        print("langchain not support gemini")

        from langchain_google_genai import ChatGoogleGenerativeAI
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp", 
            google_api_key=api_key,
            format="json"
            )
        print("Using gemini-2.0-flash-exp")
        
        # Define a Pydantic model for structured output
        class JsonOutput(BaseModel):
            """Json response output."""
            output: dict = Field(description="reply:content")

        # Bind the llm to structured output
        llm = llm.with_structured_output(JsonOutput)
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


def create_llm_chain(prompt_template: str, llm, history: str) -> str:
    """
    Creates and invokes an LLM chain using the prompt template and the history.
    """
    prompt = PromptTemplate.from_template(prompt_template)
    llm_chain = prompt | llm | StrOutputParser()
    inputs = {"history": history}
    generation = llm_chain.invoke(inputs)

    return generation