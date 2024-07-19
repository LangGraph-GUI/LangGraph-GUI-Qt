# LangGraph-GUI-backend

The backend supports running LangGraph workflow json using language models by Ollama.

This repository provides the backend for [LangGraph-GUI-Qt](https://github.com/LangGraph-GUI/LangGraph-GUI-Qt) and [LangGraph-GUI-ReactFlow](https://github.com/LangGraph-GUI/LangGraph-GUI-frontend).

*This is LangGraph-GUI backend, If you want to run in docker compose, see [LangGraph-GUI](https://github.com/LangGraph-GUI/LangGraph-GUI)*

*For a beginner-friendly introduction to LangGraph, visit [LangGraph-learn](https://github.com/LangGraph-GUI/LangGraph-learn).*

## Environment Setup

To install the required dependencies for LangGraph and server, run:
```bash
pip install -r requirements.txt
```

## Running the Application

To run a local language model, first start Ollama in a separate terminal:
```bash
ollama serve
```

### LangGraph-GUI-ReactFlow

For reactflow frontend, up the server
```bash
mkdir src/workspace
cd src/workspace
python ../server.py
```


### LangGraph-GUI-Qt

For Qt frontend, run the backend with a model such as Mistral, use the following command in another terminal:
```bash
python backend.py --graph example.json --llm gemma2 --tee output.log
```

This command will parse the specified JSON file into LangGraph components and execute result.
