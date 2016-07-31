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

import muzisapi
import pylast

help_text = 'This is muzicist bot ' \

users = TinyDB('users.json')
chats = TinyDB('chats.json')


parser = muzisapi.BaseParseClass()


# Set up logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)



# Print help text
def help(bot, update):
    """ Prints help text """
    bot.sendMessage(update.message.chat_id, text=help_text)


#starts the chat
def start(bot, update):
    """ Prints help text """

    message = update.message.to_dict()
    uid = str(message['from']["id"])
    chat_id = str(update.message.chat.id)
    username = update.message.chat.username
    query = Query()
    print("start")
    help(bot,update)
    if not chats.search(query["id"] == str(chat_id)):
        chats.insert({"id":str(chat_id),"type":update.message.chat.type,"lock":True,"quiet":False,"welcome":"hi","goodbye":"bye","users":[uid]})
    else:
        chats.update({"id":str(chat_id),"type":update.message.chat.type,"lock":True,"quiet":False,"welcome":"hi","goodbye":"bye","users":[uid]}, query.id == str(chat_id))
    # group.addUser(uid,str(users.search(query.id == str(uid))[0]["username"]),bot,update)
    # chat_id = update.message.chat.id

    # bot.sendMessage(chat_id=chat_id,
                    # text=help_text,
                    # parse_mode=ParseMode.MARKDOWN,
                    # disable_web_page_preview=True)
    keyboard = [[InlineKeyboardButton("play", callback_data='play'),InlineKeyboardButton("stop", callback_data='stop')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.sendMessage(update.message.chat_id, text="Нажмите, что бы ваши предпочтения были учитаны при составлении плейлиста", reply_markup=reply_markup)


def playlist(bot,update):
    chat_id = str(update.message.chat.id)
    query = Query()
    chat = chats.search(query.id == chat_id)[0]
    group_users = chat["users"]
    playlist = playlists[chat_id]
    for u in group_users:
        user = users.search(query.id == u)[0]
        for t in user["types"]:
            if not playlist.get(t)==None:
                playlist[t] = playlist[t]+1
            else:
                playlist[t] = 1
    
    values = ""
    for i,k in playlist.items():
        if not values == "":
            values += ","
        values+=str(i)+":"+str(int(int(k)/len(group_users)*100))

    parser.stream_from_values(values=values,size=10,operator="AND")

def push_playlist(bot,update,songs):
    bot.sendMessage(update.message.chat_id, text="Playlist", reply_markup=reply_markup)
    for s in songs:
        bot.sendAudio(update.message.chat_id, audio=parser.get(s['file_mp3']))

def button(bot, update):
    query = update.callback_query
    data = query.data
    callback[data](bot,update)

def connect(bot,update):
    query = update.callback_query
    data = query.data
    qd = query.to_dict()
    user_id = qd['from']['id']
    username = qd['from']['username']
    if addUser(user_id,username, bot, update):
        bot.sendMessage(text="@%s, вы учтены при составлении плейлиста" % (username),
                            chat_id=query.message.chat_id)
    # else:
        # bot.sendMessage(text="@%s, вы уже были учтены при составлении плейлиста" % (username),
                            # chat_id=query.message.chat_id)


callback = {"connect":connect}

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


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN, workers=2)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler('welcome', set_welcome))
    dp.add_handler(CommandHandler('goodbye', set_goodbye))
    dp.add_handler(CommandHandler('disable_goodbye', disable_goodbye))
    dp.add_handler(CommandHandler("lock", lock))
    dp.add_handler(CommandHandler("unlock", unlock))
    dp.add_handler(CommandHandler("quiet", quiet))
    dp.add_handler(CommandHandler("unquiet", unquiet))
    dp.add_handler(CommandHandler("playlist", playlist))
    
    dp.add_handler(CallbackQueryHandler(button))
    # dp.add_handler(StringRegexHandler('^$', empty_message))
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
