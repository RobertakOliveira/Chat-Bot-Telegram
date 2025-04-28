import sys
import os

# 👉 Ajusta o PYTHONPATH antes de tudo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask
from controllers.main_controller import Main, ProcessQuery

app = Flask(__name__)

# Rota de saúde
@app.route("/", methods=["GET"])
def main():
    return Main()

# Rota de consulta RAG
@app.route("/query", methods=["POST"])
def process_query():
    return ProcessQuery()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
