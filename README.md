# LangGraph-GUI


## Environment

### front-end GUI
```
pip install PySide6
```

## Run

### front-end

```
python frontend.py
```
and you can read and write json file as DAG graph for crewai.

### back-end
if local run such mistral

```
python backend.py --graph example.json --llm mistral --tee output.log
```
it will parse json file into crewai tasks and agents



## Build
### front-end GUI
remember hook 

```
pip install pyinstaller

cd src
pyinstaller --onefile --additional-hooks-dir=. frontend.py
```