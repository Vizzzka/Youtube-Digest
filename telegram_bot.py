from telegram.ext.updater import Updater
from telegram.update import Update
from telegram import ParseMode
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
import urllib.parse
from google.cloud import bigquery
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
    data = json.loads(f.read())

    message = from_json_to_tg_digest(data)
    id = 264147190
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