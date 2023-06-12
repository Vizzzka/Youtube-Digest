from datetime import datetime
from google.cloud import storage
import telegram
from telegram import ParseMode
import json
import os
from utils import *
import schedule
import time


def send_digest():
    api_key = os.environ.get("TELEGRAM_API_TOKEN")
    bot = telegram.Bot(token=api_key)
    storage_client = storage.Client()

    bucket_name = "youtube-digests"
    blobs = storage_client.list_blobs(bucket_name, prefix="2023/{}/{}".format(datetime.now().month, datetime.now().day))

    # Note: The call returns a response only when the iterator is consumed.
    for blob in blobs:
        json_digest = json.loads(blob.download_as_string())
        json_digest["videos"] = sorted(json_digest["videos"], key=lambda a: a["views"], reverse=True)[:4]
        file_data = from_json_to_tg_digest(json_digest)
        chat_id = blob.name.split("-")[1].split(".")[0]
        bot.send_message(chat_id=chat_id, text=file_data, parse_mode=ParseMode.HTML)


if __name__ == "__main__":
    schedule.every().day.at("20:00").do(send_digest)
    while True:
        schedule.run_pending()
        time.sleep(1)