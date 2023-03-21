# Python Imports #
import os
import datetime

# Third Party Imports #
from flask import Flask, render_template

# water-tank-monitor Imports #
from api_helpers import get_api_tank_data, get_openweather_api, get_details_from_api

app = Flask(__name__, template_folder="./_flask_templates", static_folder="./_flask_static")


@app.route("/tank_data")
def get_tank_data() -> dict:
    _TANK_URL = "http://" + os.environ.get("TANK_API_URL") + "/distance"
    tank_data = get_api_tank_data(_TANK_URL)
    return tank_data


@app.route("/tank_history")
def get_tank_history() -> dict:
    _TANK_URL = "http://" + os.environ.get("TANK_API_URL") + "/history"
    percentage_history = []
    timestamp_history = []
    tank_history = get_api_tank_data(_TANK_URL)
    for metric in tank_history["history"]:
        percentage_history.append(metric["percentage"])
        timestamp_history.append(str(datetime.datetime.fromtimestamp(int(metric["timestamp"]))))
    return {
        "percentage_history": percentage_history,
        "timestamp_history": timestamp_history
    }


@app.route("/")
def dashboard():
    _CITY = os.environ.get("OPENWEATHERMAP_CITY")
    _OWM_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")

    tank_data = get_tank_data()

    api_res = get_openweather_api(_CITY, _OWM_KEY)
    weather_data = get_details_from_api(api_res)
    weather_data["curr_loc"] = _CITY
    return render_template("index.html", weather_data=weather_data, tank_data=tank_data)


def main():
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    main()

