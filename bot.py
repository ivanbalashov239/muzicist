#!/usr/bin/env python3
import logging

import sys
from telegram import Emoji, ParseMode, TelegramError, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, StringRegexHandler,
                          ConversationHandler, StringCommandHandler, CallbackQueryHandler, )
# from telegram.dispatcher import run_async
from tinydb import TinyDB, Query, operations
import traceback
import json
import group
import personal
import config

import muzisapi
# Set up logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

handler ={
        "start":{
            "group":group.start,
            "supergroup":group.start,
            "personal":personal.start,
            },
        "help":{
            "group":group.help,
            "supergroup":group.help,
            "personal":personal.help,
            },
        "button":{
            "group":group.button,
            "supergroup":group.button,
            "personal":personal.button,
            },
        }


def error(bot, update, error, **kwargs):
    """ Error handling """

    try:
        if isinstance(error, TelegramError)\
                and error.message == "Unauthorized"\
                or "PEER_ID_INVALID" in error.message\
                and isinstance(update, Update):
                    chats.remove(Query().id == update.message.chat_id)
                    logger.info('Removed chat_id %s from chat list' % update.message.chat_id)
        else:
            logger.error("An error (%s) occurred: %s"
                         % (type(error), error.message))
    except:
        pass
def start(bot,update):
    handler["start"][update.message.chat.type](bot,update)

def help(bot,update):
    handler["help"][update.message.chat.type](bot,update)

def playlist(bot,update):
    handler["playlist"][update.message.chat.type](bot,update)

def button(bot,update):
    handler["button"][update.callback_query.message.chat.type](bot,update)

def empty_message(bot, update):
    bot.sendMessage(update.message.chat_id, text="empty")

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.TOKEN, workers=config.WORKERS)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("playlist", playlist))
    
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(StringRegexHandler('^$', empty_message))
    # dp.add_handler(StringCommandHandler('', empty_message))

    # dp.add_handler(StringCommandHandler('level', set_log_level))
    # dp.add_handler(StringCommandHandler('count', chatcount))

    dp.add_error_handler(error)

    # Start the Bot and store the update Queue, so we can insert updates
    update_queue = updater.start_polling(poll_interval=1, timeout=5)

    # Alternatively, run with webhook:
    # updater.bot.setWebhook(webhook_url='https://%s/%s' % (BASE_URL, TOKEN))
    # Or, if SSL is handled by a reverse proxy, the webhook URL is already set
    # and the reverse proxy is configured to deliver directly to port 6000:
    # update_queue = updater.start_webhook(HOST, PORT, url_path=TOKEN)
    # update_queue = updater.start_webhook(listen=HOST,
                      # port=PORT,
                      # url_path=TOKEN,
                      # key=CERT_KEY,
                      # cert=CERT,
                      # webhook_url='https://%s/%s' % (BASE_URL, TOKEN))

    # Start CLI-Loop
    while True:
        text = input()

        # Gracefully stop the event handler
        if text == 'stop':
            updater.stop()
            break

        # else, put the text into the update queue
        elif len(text) > 0:
            update_queue.put(text)  # Put command into queue

if __name__ == '__main__':
    main()
