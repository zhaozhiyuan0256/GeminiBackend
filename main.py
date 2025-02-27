from datetime import datetime, timezone
from gemini_app import app, czmlManager

TLE_FILEPATH = "./data/three.tle"
GROUND_EQUIPMENTS_FILEPATH = "./data/facilities.json"


if __name__ == "__main__":
    czmlManager.init(
        TLE_FILEPATH, GROUND_EQUIPMENTS_FILEPATH
    )
    app.run()

import tle2czml