# LangGraph-GUI-backend

The backend supports running LangGraph-GUI workflow json using language models by Ollama.

For more infomation, please see official site: [LangGraph-GUI.github.io](https://LangGraph-GUI.github.io)

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

At another thread, up the server
```bash
mkdir src/workspace
cd src/workspace
python ../server.py
```