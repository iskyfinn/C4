from flask import Flask, jsonify
from C1 import C4ContextDiagram
from C2 import C4ContainerDiagram
from C3 import C4ComponentDiagram
from C4 import C4CodeDiagram

app = Flask(__name__)

@app.route('/api/c1')
def get_c1():
    diagram = C4ContextDiagram("Online Shopping Application")
    # (populate it or load from a saved source)
    return jsonify(diagram.to_json())

@app.route('/api/c2')
def get_c2():
    diagram = C4ContainerDiagram("Online Shopping Application")
    # (populate it)
    return jsonify(diagram.to_json())

@app.route('/api/c3')
def get_c3():
    diagram = C4ComponentDiagram("API Application")
    # (populate it)
    return jsonify(diagram.to_json())

@app.route('/api/c4')
def get_c4():
    diagram = C4CodeDiagram("Order Management Controller")
    # (populate it)
    return jsonify(diagram.to_json())

if __name__ == '__main__':
    app.run(debug=True)
