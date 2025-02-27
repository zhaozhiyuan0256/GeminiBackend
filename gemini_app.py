from flask import Flask
from flask_cors import CORS
from czml import CZMLManager

app = Flask("GeminiBackend")
CORS(app)

czmlManager = CZMLManager()


@app.route("/api/hello")
def hello():
    return {"message": "hello"}


@app.route("/api/environment")
def get_environment():
    czmlManager.refresh()
    return {"message": "environment", "data": czmlManager.get_environment()}


@app.route("/api/route")
def get_route():
    return {"message": "route", "data": czmlManager.get_route()}
