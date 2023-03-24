# Python Imports #
import os
import time
import asyncio
import datetime
import threading

# Third Party Imports #
from flask import Flask, render_template
from dotenv import load_dotenv

# water-tank-monitor Imports #
from helpers.api_helpers import get_api_tank_data, get_openweather_api, get_details_from_api
from helpers.notification_helpers import send_notification

load_dotenv()
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


async def main():
    _BOT_TOKEN = str(os.environ.get("TELEGRAM_BOT_TOKEN"))
    _TELEGRAM_CHATID = os.environ.get("TELEGRAM_CHAT_ID")
    _API_IP_ENDPOINT = f"""http://{os.environ.get("TANK_API_URL")}/distance"""
    _TANK_TRESHOLD = int(os.environ.get("TANK_TRESHOLD"))

    loop = asyncio.get_event_loop()

    # Start the Flask app
    app_task = loop.run_in_executor(None, app.run, "0.0.0.0")

    # Start the send_notification coroutine
    notification_task = asyncio.create_task(
        send_notification(_BOT_TOKEN, _API_IP_ENDPOINT, _TELEGRAM_CHATID, _TANK_TRESHOLD)
    )

    notification_task = asyncio.create_task(
        send_notification(_BOT_TOKEN, _API_IP_ENDPOINT, _TELEGRAM_CHATID, _TANK_TRESHOLD)
    )

    # Wait for both tasks to finish
    await asyncio.gather(app_task, notification_task)


if __name__ == "__main__":
    asyncio.run(main())

