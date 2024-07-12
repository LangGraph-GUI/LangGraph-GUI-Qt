# LangGraph-GUI-backend

This repository provides the backend for [LangGraph-GUI-Qt](../../LangGraph-GUI-Qt) and [LangGraph-GUI-ReactFlow](../../LangGraph-GUI).

The backend supports running workflows locally using language models by Ollama.

*For a beginner-friendly introduction to LangGraph, visit [LangGraph-learn](../../LangGraph-learn).*

## Environment Setup

To install the required dependencies for LangGraph, run:
```bash
pip install langchain langchain-community langchain-core langgraph
```

## Running the Application

To run a local language model, first start Ollama in a separate terminal:
```bash
ollama serve
```

Then, to run the backend with a model such as Mistral, use the following command in another terminal:
```bash
python backend.py --graph example.json --llm gemma2 --tee output.log
```

This command will parse the specified JSON file into LangGraph components and execute result.

