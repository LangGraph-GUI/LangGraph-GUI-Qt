# LangGraph-GUI

LangGraph-GUI is a user-friendly interface for managing and visualizing Node-Edge workflows with LangGraph. It supports creating, editing, and running workflows locally using language models by Ollama .

This is node-edge based gui will export to json for better decoupling.

![LangGraph-GUI](cover.webp)


## Environment Setup

### Front-End GUI

To install the required dependencies for the front-end GUI, run:
```bash
pip install PySide6
```

## Running the Application

### Front-End

To start the front-end GUI, execute:
```bash
python frontend.py
```
This will allow you to read and write JSON files representing DAG workflows for CrewAI.

### Back-End

To run the back-end locally with a language model like Mistral, use:
```bash
python backend.py --graph example.json --llm mistral --tee output.log
```
This command will parse the specified JSON file into CrewAI tasks and agents.

## Building the Application

### Front-End GUI

To build the front-end GUI into a standalone executable, follow these steps:

1. Install PyInstaller:
    ```bash
    pip install pyinstaller
    ```

2. Navigate to the source directory:
    ```bash
    cd src
    ```

3. Run PyInstaller with the necessary hooks:
    ```bash
    pyinstaller --onefile --additional-hooks-dir=. frontend.py
    ```

By following these instructions, you can easily set up, run, and build the LangGraph-GUI 

## Other Resource
If you want to learn LangGraph, we have LangGraph for dummy learning : [LangGraph-learn](../LangGraph-learn)