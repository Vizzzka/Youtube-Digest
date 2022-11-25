from telegram.ext.updater import Updater
from telegram.update import Update
from telegram import ParseMode
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
import urllib.parse

from authorize_user import authorization_url


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hello! It is daily Youtube digest Bot. If u want to receive daily updates please login into your account.")


def help(update: Update, context: CallbackContext):
    update.message.reply_text("This bot is scheduled to send you daily Youtube digest at 20:00 based on your"
                              " subscriptions. To do this you need to login into your account with /login command."
                              "\n If you want to unsubscribe use /logout command."
                              "\n If you want to change schedule time use /change_time xx:00 command"
                              " where xx is prefered hour.")


def login(update: Update, context: CallbackContext):
    new_authorizatoin_url = authorization_url.replace(authorization_url.split('&')[4], "state={}".format(str(update.message.chat_id)))
    print(new_authorizatoin_url)
    update.message.reply_text(text="<a href='{0}'>login</a>".format(new_authorizatoin_url), parse_mode=ParseMode.HTML)


if __name__ == "__main__":

    updater = Updater("5518802812:AAHl0feaoMycYUgpNukDJUQFiLLJztTBWtA",
                      use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('login', login))
    # print(authorization_url)
    updater.start_polling()