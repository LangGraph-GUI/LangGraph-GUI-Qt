# LangGraph-GUI


## Environment

### front-end GUI
```
pip install PySide6
```


## Build
### front-end GUI
remember hook 

```
pip install pyinstaller

cd src
pyinstaller --onefile --additional-hooks-dir=. frontend.py
```