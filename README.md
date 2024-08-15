# LangGraph-GUI-backend

This is old version for langgraph-gui, json format need [examples v0.5.8](https://github.com/LangGraph-GUI/examples/tree/v0.5.8)

The backend supports running LangGraph-GUI workflow json using localLLM such ollama.

## Environment Setup

To install the required dependencies for LangGraph and server, run:
```bash
pip install -r requirements.txt
```

## Running the server

To run a local language model, first start Ollama in a separate terminal:
```bash
ollama serve
```

At another thread, up the server
```bash
mkdir src/workspace
cd src/workspace
python ../server.py
```
