import os
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram import ParseMode
from google.auth.transport.requests import Request
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
import googleapiclient.discovery
import googleapiclient.errors
import json
from utils import *

from authorize_user import authorization_url


scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
TG_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hello! It is daily Youtube digest Bot. If u want to receive daily updates please login into your account."
        "\n So that it would be possible to get your subscriptions. You would be asked only for read-only access."
        "After authorization you would receive daily digests, also you can get full list of your subscriptions. \n"
        "In case you are not authorized you are still able to get trending videos in your country."
        "\n For more information use help command.")


def help(update: Update, context: CallbackContext):
    update.message.reply_text("This bot is scheduled to send you daily Youtube digest at 20:00 based on your"
                              " subscriptions. To do this you need to login into your account with /login command."
                              "\n If you want to unsubscribe use /logout command."
                              "\n If you want to change schedule time to 10:00 AM use /change_time command"
                              "\n If you just want to receive trending videos in your country use /trends command "
                              "\n If you want to get all your subsciptions channels use /subscriptions command")


def trends(update: Update, context: CallbackContext):

    api_service_name = "youtube"
    api_version = "v3"
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    youtube = googleapiclient.discovery.build(api_service_name, api_version)

    request = youtube.videos().list(
        part="contentDetails,snippet,statistics",
        maxResults=3,
        chart="mostPopular",
        key=GOOGLE_API_KEY,
        regionCode="UA"
    )
    data = {"videos": [{"name": "", "channel_name": "", "views": "", "number_in_trends": 1, "likes": "", "top_comment": "", "link_to_video": ""},
                       {"name": "", "channel_name": "", "views": "", "number_in_trends": 2, "likes": "", "top_comment": "", "link_to_video": ""},
                       {"name": "", "channel_name": "", "views": "", "number_in_trends": 3, "likes": "",
                        "top_comment": "", "link_to_video": ""}]}

    response = request.execute()
    data["videos"][0]["name"] = response["items"][0]["snippet"]["title"]
    data["videos"][1]["name"] = response["items"][1]["snippet"]["title"]
    data["videos"][2]["name"] = response["items"][2]["snippet"]["title"]

    data["videos"][0]["link_to_video"] = "https://www.youtube.com/watch?v={}".format(response["items"][0]["id"])
    data["videos"][1]["link_to_video"] = "https://www.youtube.com/watch?v={}".format(response["items"][1]["id"])
    data["videos"][2]["link_to_video"] = "https://www.youtube.com/watch?v={}".format(response["items"][2]["id"])

    data["videos"][0]["views"] = response["items"][0]["statistics"]["viewCount"]
    data["videos"][0]["likes"] = response["items"][0]["statistics"].get("likeCount", 0)
    data["videos"][1]["views"] = response["items"][1]["statistics"]["viewCount"]
    data["videos"][1]["likes"] = response["items"][1]["statistics"].get("likeCount", 0)
    data["videos"][2]["views"] = response["items"][2]["statistics"]["viewCount"]

    data["videos"][0]["likes"] = response["items"][0]["statistics"].get("likeCount", 0)
    data["videos"][1]["likes"] = response["items"][1]["statistics"].get("likeCount", 0)
    data["videos"][2]["likes"] = response["items"][2]["statistics"].get("likeCount", 0)

    data["videos"][0]["channel_name"] = response["items"][0]["snippet"]["channelTitle"]
    data["videos"][1]["channel_name"] = response["items"][1]["snippet"]["channelTitle"]
    data["videos"][2]["channel_name"] = response["items"][2]["snippet"]["channelTitle"]

    request = youtube.commentThreads().list(
        part="snippet",
        maxResults=1,
        key=GOOGLE_API_KEY,
        videoId=response["items"][0]["id"],
        order="relevance"
    )

    response2 = request.execute()
    data["videos"][0]["top_comment"] = response2["items"][0]["snippet"]["topLevelComment"]["snippet"]["textOriginal"].split("\n")[0]

    request = youtube.commentThreads().list(
        part="snippet",
        maxResults=1,
        key=GOOGLE_API_KEY,
        videoId=response["items"][1]["id"],
        order="relevance"
    )

    response2 = request.execute()
    data["videos"][1]["top_comment"] = response2["items"][0]["snippet"]["topLevelComment"]["snippet"]["textOriginal"].split("\n")[0]

    request = youtube.commentThreads().list(
        part="snippet",
        maxResults=1,
        key=GOOGLE_API_KEY,
        videoId=response["items"][2]["id"],
        order="relevance"
    )

    response2 = request.execute()
    data["videos"][2]["top_comment"] = response2["items"][0]["snippet"]["topLevelComment"]["snippet"]["textOriginal"].split("\n")[0]

    message = from_json_to_tg_digest(data)
    update.message.reply_text(text=message, parse_mode=ParseMode.HTML)


def get_subscriptions(update: Update, context: CallbackContext):
    db_client = bigquery.Client()
    chat_id = update.message.chat_id
    query_job = db_client.query("SELECT chat_id, token, subscription_date FROM DigestStorage.Users WHERE chat_id={}".format(str(chat_id)))
    result = query_job.result()
    for r in result:
        row = []
        for r2 in r:
            row.append(r2)
        credentials_dct = row[1]

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    creds = Credentials.from_authorized_user_info(json.loads(credentials_dct), scopes)
    if creds.expired:
        print("expired")
        creds.refresh(Request())
        # write cred to db
        update_creds(chat_id, creds, db_client)

    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=creds)

    request = youtube.subscriptions().list(
        part="snippet",
        maxResults=40,
        mine=True
    )
    response = request.execute()
    message = [(item["snippet"]["title"], item["snippet"]["resourceId"]["channelId"]) for item in response["items"]]
    message = form_channel_list(message)
    update.message.reply_text(text=message, parse_mode=ParseMode.HTML)
    print(response)
    return response


def form_channel_list(lst):
    result = ""
    for channel in lst:
        result = result + "<a href='{}'>{}</a>\n".format("https://www.youtube.com/channel/{}".format(channel[1]), channel[0])

    return result


def login(update: Update, context: CallbackContext):
    print(update.message.chat_id)
    new_authorizatoin_url = authorization_url.replace(authorization_url.split('&')[4], "state={}".format(str(update.message.chat_id)))
    update.message.reply_text(text="To login please click the <a href='{0}'>link</a> and provide access for the bot to see your subscriptions."
                                   "*During login please click 'Advanced settings' and give access. It is needed because app is in test mode and not published yet.".format(new_authorizatoin_url), parse_mode=ParseMode.HTML)


def logout(update: Update, context: CallbackContext):
    update.message.reply_text(text="You successfully unsubscribed from digests. To subscribe again use /login command.", parse_mode=ParseMode.HTML)


def change_time(update: Update, context: CallbackContext):
    update.message.reply_text(text="You successfully changed digest time to 10:00 AM. To change the time to 8:00 PM use this command again.", parse_mode=ParseMode.HTML)


if __name__ == "__main__":
    updater = Updater(TG_TOKEN, use_context=True)
    j = updater.job_queue
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('login', login))
    updater.dispatcher.add_handler(CommandHandler('trends', trends))
    updater.dispatcher.add_handler(CommandHandler('change_time', change_time))
    updater.dispatcher.add_handler(CommandHandler('subscriptions', get_subscriptions))

    # print(authorization_url)
    updater.start_polling()
    updater.idle()