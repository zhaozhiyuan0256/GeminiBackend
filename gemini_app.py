from datetime import datetime, timezone
from flask import Flask
from flask_cors import CORS
from czml_manager import CZMLManager
from topology import Topology

TLES_FILEPATH = "./data/three.tle"
FACILITIES_FILEPATH = "./data/facilities.json"
ISLS_FILEPATH = "./data/three.isls"


app = Flask("GeminiBackend")
CORS(app)

czmlManager = CZMLManager()
czmlManager.init(TLES_FILEPATH, FACILITIES_FILEPATH)
topology = Topology(TLES_FILEPATH, FACILITIES_FILEPATH, ISLS_FILEPATH)


@app.route("/api/hello")
def hello():
    return {"message": "hello"}


@app.route("/api/mobility")
def get_environment():
    czmlManager.refresh()
    return {"message": "mobility", "data": czmlManager.get_mobility()}


@app.route("/api/path")
def get_route():
    node_name_list = ["ue-1", "gemini-1", "core-1"]
    return {
        "message": "route",
        "data": czmlManager.get_paths_czml_by_time_range(
            topology, node_name_list, datetime.now(tz=timezone.utc), 15
        ),
    }


@app.route("/api/all")
def get_all():
    czmlManager.refresh()
    node_name_list = ["ue-1", "gemini-1", "core-1"]
    # print(czmlManager.get_mobility())
    # print(
    #     czmlManager.get_paths_czml_by_time_range(
    #         topology, node_name_list, datetime.now(tz=timezone.utc), 15
    #     )
    # )
    return {
        "message": "all",
        "data": czmlManager.get_mobility()
        + czmlManager.get_paths_czml_by_time_range(
            topology, node_name_list, datetime.now(tz=timezone.utc),60
        ),
    }
