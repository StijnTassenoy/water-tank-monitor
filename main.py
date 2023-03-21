# Python Imports #
import os

# Third Party Imports #
from flask import Flask, render_template

# water-tank-monitor Imports #
from api_helpers import get_current_tank_details, get_openweather_api, get_details_from_api

app = Flask(__name__, template_folder="./_flask_templates", static_folder="./_flask_static")


@app.route("/")
def dashboard():
    _CITY = os.environ.get("OPENWEATHERMAP_CITY")
    _OWM_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")
    _TANK_URL = "http://" + os.environ.get("TANK_API_URL") + "/distance"

    tank_data = get_current_tank_details(_TANK_URL)

    api_res = get_openweather_api(_CITY, _OWM_KEY)
    weather_data = get_details_from_api(api_res)
    weather_data["curr_loc"] = _CITY
    return render_template("index.html", weather_data=weather_data, tank_data=tank_data)


def main():
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    main()

