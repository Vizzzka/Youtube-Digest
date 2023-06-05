from datetime import datetime
from google.cloud import storage
import telegram
from telegram import ParseMode
import json


def from_json_to_tg_digest(digest_json):
    result = ""
    for video in digest_json["videos"]:
        s = "\U000027A1  <a href='{}'>{}</a> {} \n \U0001F440 <b>{} views</b> \n \U0001F44D <b> {} likes </b> \n \U0001F525 {} in trends \n \U0001F4E2 <i>{}</i> \n \n".format(video["link_to_video"],
                                   video["name"],
                                   video["channel_name"],
                                   number_of_views(video["views"]),
                                   number_of_views(video["likes"]),
                                   number_in_trend(video["number_in_trends"]),
                                   video["top_comment"])
        result = result + s
    return result


def number_in_trend(number):
    if number is None:
        return "Not"
    else:
        return number


def number_of_views(views):
    views=int(views)
    if views > 1000000:
        return str(views // 1000000) + "M"
    else:
        if views > 1000:
            return str(views / 1000) + "k"
        else:
            return str(views)

def send_digest():
    api_key = "5518802812:AAHl0feaoMycYUgpNukDJUQFiLLJztTBWtA"
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
    send_digest()