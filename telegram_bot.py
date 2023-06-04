from telegram.ext.updater import Updater
from telegram.update import Update
from telegram import ParseMode
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
import googleapiclient.discovery
import googleapiclient.errors
import datetime
import json
import pytz

from authorize_user import authorization_url


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hello! It is daily Youtube digest Bot. If u want to receive daily updates please login into your account.")


def help(update: Update, context: CallbackContext):
    update.message.reply_text("This bot is scheduled to send you daily Youtube digest at 20:00 based on your"
                              " subscriptions. To do this you need to login into your account with /login command."
                              "\n If you want to unsubscribe use /logout command."
                              "\n If you want to change schedule time to 10:00 AM use /change_time command"
                              "\n If you just want to receive trending videos use /trends command")


def trends(update: Update, context: CallbackContext):

    f = open('trends.json', "r", encoding='utf-8')
    # Reading from file
    data = {"videos": [{"name": "", "channel_name": "", "views": "", "number_in_trends": 1, "likes": "", "top_comment": "", "link_to_video": ""},
                       {"name": "", "channel_name": "", "views": "", "number_in_trends": 1, "likes": "", "top_comment": "", "link_to_video": ""},
                       {"name": "", "channel_name": "", "views": "", "number_in_trends": 1, "likes": "",
                        "top_comment": "", "link_to_video": ""}
                        ],
                "client_id":  "1066834567857-8flsq25qm601hgibojsjvspetvho8ula",
                "chat_id": 264147190,
                "timestamp": 1689393
            }
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(api_service_name, api_version)

    request = youtube.videos().list(
        part="contentDetails,snippet,statistics",
        maxResults=3,
        chart="mostPopular",
        key="AIzaSyC_pggkHUySm4NAzXUj652Pjrzckqb-_Ks",
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
    data["videos"][0]["likes"] = response["items"][0]["statistics"]["likeCount"]
    data["videos"][1]["views"] = response["items"][1]["statistics"]["viewCount"]
    data["videos"][1]["likes"] = response["items"][1]["statistics"]["likeCount"]
    data["videos"][2]["views"] = response["items"][2]["statistics"]["viewCount"]
    print(response["items"][2]["statistics"])
    data["videos"][2]["likes"] = response["items"][2]["statistics"].get("likeCount", 0)

    data["videos"][0]["channel_name"] = response["items"][0]["snippet"]["channelTitle"]
    data["videos"][1]["channel_name"] = response["items"][1]["snippet"]["channelTitle"]
    data["videos"][2]["channel_name"] = response["items"][2]["snippet"]["channelTitle"]

    request = youtube.commentThreads().list(
        part="snippet",
        maxResults=1,
        key="AIzaSyC_pggkHUySm4NAzXUj652Pjrzckqb-_Ks",
        videoId=response["items"][0]["id"],
        order="relevance"
    )

    response2 = request.execute()
    data["videos"][0]["top_comment"] = response2["items"][0]["snippet"]["topLevelComment"]["snippet"]["textOriginal"]


    request = youtube.commentThreads().list(
        part="snippet",
        maxResults=1,
        key="AIzaSyC_pggkHUySm4NAzXUj652Pjrzckqb-_Ks",
        videoId=response["items"][1]["id"],
        order="relevance"
    )

    response2 = request.execute()
    data["videos"][1]["top_comment"] = response2["items"][0]["snippet"]["topLevelComment"]["snippet"]["textOriginal"]

    request = youtube.commentThreads().list(
        part="snippet",
        maxResults=1,
        key="AIzaSyC_pggkHUySm4NAzXUj652Pjrzckqb-_Ks",
        videoId=response["items"][2]["id"],
        order="relevance"
    )

    response2 = request.execute()
    data["videos"][2]["top_comment"] = response2["items"][0]["snippet"]["topLevelComment"]["snippet"]["textOriginal"]


    message = from_json_to_tg_digest(data)
    update.message.reply_text(text=message, parse_mode=ParseMode.HTML)


def login(update: Update, context: CallbackContext):
    print(update.message.chat_id)
    new_authorizatoin_url = authorization_url.replace(authorization_url.split('&')[4], "state={}".format(str(update.message.chat_id)))
    print(new_authorizatoin_url)
    update.message.reply_text(text="To login please click the <a href='{0}'>link</a> and provide access for the bot to see your subscriptions.".format(new_authorizatoin_url), parse_mode=ParseMode.HTML)


def logout(update: Update, context: CallbackContext):
    update.message.reply_text(text="You successfully unsubscribed from digests. To subscribe again use /login command.", parse_mode=ParseMode.HTML)


def change_time(update: Update, context: CallbackContext):
    update.message.reply_text(text="You successfully changed digest time to 10:00 AM. To change the time to 8:00 PM use this command again.", parse_mode=ParseMode.HTML)


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


def number_of_views(views):
    print(views)
    views=int(views)
    if views > 1000000:
        return str(views // 1000000) + "M"
    else:
        return str(views / 1000) + "k"


def number_in_trend(number):
    if number is None:
        return "Not"
    else:
        return number


def daily_report(context: CallbackContext):
    f = open('digest_example.json', "r", encoding='utf-8')
    # Reading from file
    data = json.loads(f.read())

    message = from_json_to_tg_digest(data)
    id = 264147190
    context.bot.send_message(chat_id=id, text=message, parse_mode=ParseMode.HTML)


if __name__ == "__main__":

    updater = Updater("5518802812:AAHl0feaoMycYUgpNukDJUQFiLLJztTBWtA",
                      use_context=True)

    j = updater.job_queue
    j.run_daily(daily_report, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=16, minute=24, second=00, tzinfo=pytz.timezone('Europe/Kiev')))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('login', login))
    updater.dispatcher.add_handler(CommandHandler('trends', trends))
    updater.dispatcher.add_handler(CommandHandler('change_time', change_time))

    # print(authorization_url)
    updater.start_polling()
    updater.idle()