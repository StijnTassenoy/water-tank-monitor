# Python Imports #
import time
import datetime

# Third Party Imports #
import requests


def get_current_tank_details(tank_url: str) -> dict:
    res = requests.get(tank_url)
    return res.json()


def get_openweather_api(city: str, api_key: str) -> dict:
    owm_api_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}"

    res = requests.get(owm_api_url)
    return res.json()


def get_details_from_api(api_res: dict) -> dict:
    timestamp = int(time.time())
    temp = float(api_res["list"][0]["main"]["temp"])
    temp_in_c = float("{:.2f}".format(temp - 273.15))
    if api_res["list"][0].get("rain"):
        curr_precipitation = "Rain precipitation: " + api_res["list"][0]["rain"]["3h"]
    elif api_res["list"][0].get("snow"):
        curr_precipitation = "Snow precipitation: " + api_res["list"][0]["snow"]["3h"]
    else:
        curr_precipitation = "No precipitation"
    return {
        "curr_timestamp": str(timestamp),
        "curr_date": str(datetime.datetime.fromtimestamp(timestamp)),
        "curr_weather": api_res["list"][0]["weather"][0]["description"],
        "curr_temperature": f"{temp_in_c}°C",
        "curr_precipitation": curr_precipitation,
    }