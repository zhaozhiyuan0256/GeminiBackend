from datetime import datetime, timezone
from topology import Topology
from gemini_app import app


if __name__ == "__main__":
    app.run(host="192.168.160.134", port=5000)
