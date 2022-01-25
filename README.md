# bpmnviz
A simple visualization tool for BPMN flow diagrams using Graphviz/Dot


## dependencies

- Python3
- Virtual Env
- Graphviz

## installation

- create and activate python virtual environment
```
virtualenv -p python3 env
. env/bin/activate
```

- install libraries
```
pip install -r requirements.txt
```

## usage

- you can check the command line help at any time:

```
python3 bpmnviz.py --help
```

- piping is a convenient way to use it (image magick is assumed):
```
cat somebpmn.xml | python3 bpmnviz.py | dot -Tpng | display
```
