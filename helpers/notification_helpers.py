# Python Imports #
import asyncio
import os
import time
import datetime

# Third Party Imports #
import requests
import telegram
from telegram import Update
from telegram.ext import CallbackContext


async def get_notified(bot_token: str, api_ip_endpoint: str, chat_id: str, treshold: int) -> None:
    bot = telegram.Bot(token=bot_token)
    try:
        response = requests.get(api_ip_endpoint)
        tank_data = response.json()
        percentage = tank_data["percentage"]
        print(f"Tank percentage: {percentage}")
        if int(percentage) > treshold:
            await bot.send_message(chat_id=chat_id, text="Tank percentage is higher than 75%!")
    except requests.exceptions.RequestException as e:
        print("Error getting data from API:", e)


async def send_notification(bot_token: str, api_ip_endpoint: str, chat_id: str, threshold: int) -> None:
    while True:
        now = datetime.datetime.now()
    # if now.minute == 0:     # If the current time is at the start of the hour
        print(f"[i] {now}: get_notified is running")
        await get_notified(bot_token, api_ip_endpoint, chat_id, threshold)
        await asyncio.sleep(5)     # Sleep for 1 minute before checking again
