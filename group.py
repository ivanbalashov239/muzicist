#!/usr/bin/env python3
help_text = 'Welcomes everyone that enters a group chat that this bot is a ' \
            'part of. By default, only the person who invited the bot into ' \
            'the group is able to change settings.\nCommands:\n\n' \
            '/welcome - Set welcome message\n' \
            '/goodbye - Set goodbye message\n' \
            '/disable\\_goodbye - Disable the goodbye message\n' \
            '/lock - Only the person who invited the bot can change messages\n'\
            '/unlock - Everyone can change messages\n\n' \
            'You can use _$username_ and _$title_ as placeholders when setting'\
            ' messages.\n' \
            'Please [rate me](http://storebot.me/bot/examplebot) :) ' \
            'Questions? Message my creator @exampleuser'
import logging

import sys
from telegram import Emoji, ParseMode, TelegramError, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, StringRegexHandler,
                          ConversationHandler, StringCommandHandler, CallbackQueryHandler, )
# from telegram.dispatcher import run_async
from tinydb import TinyDB, Query, operations
import traceback
import json

import muzisapi

help_text = 'Welcomes everyone that enters a group chat that this bot is a ' \
            'part of. By default, only the person who invited the bot into ' \
            'the group is able to change settings.\nCommands:\n\n' \
            '/welcome - Set welcome message\n' \
            '/goodbye - Set goodbye message\n' \
            '/disable\\_goodbye - Disable the goodbye message\n' \
            '/lock - Only the person who invited the bot can change messages\n'\
            '/unlock - Everyone can change messages\n\n' \
            'You can use _$username_ and _$title_ as placeholders when setting'\
            ' messages.\n' \
            'Please [rate me](http://storebot.me/bot/examplebot) :) ' \
            'Questions? Message my creator @exampleuser'

# Create database object
chats = TinyDB('chats.json')
users = TinyDB('users.json')

# playlists={}

parser = muzisapi.BaseParseClass()

q = Query()

# Set up logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)






# Print help text
def help(bot, update):
    """ Prints help text """

    chat_id = update.message.chat.id

    # bot.sendMessage(chat_id=chat_id,
                    # text=help_text,
                    # parse_mode=ParseMode.MARKDOWN,
                    # disable_web_page_preview=True)
    keyboard = [[InlineKeyboardButton("Подключиться", callback_data='connect')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.sendMessage(update.message.chat_id, text="Нажмите, что бы ваши предпочтения были учитаны при составлении плейлиста", reply_markup=reply_markup)

#starts the chat
def start(bot, update):
    """ Prints help text """

    print("start")
    chat_id = update.message.chat.id
    query = Query()
    # playlists[str(chat_id)] = {}
    if not chats.search(query["id"] == str(chat_id)):
        chats.insert({"id":str(chat_id),"type":update.message.chat.type,"lock":True,"quiet":False,"welcome":"hi","goodbye":"bye","users":[]})
    else:
        chats.update({"type":update.message.chat.type}, query.id == str(chat_id))
    help(bot,update)

def addUser(uid,name,bot,update):
    query=Query()
    uid = str(uid)
    groupid = str(update.callback_query.message.chat.id)
    if not users.search(query["id"] == uid):
        users.insert({"id":uid,"username":name,"types":[]})
    else:
        users.update({"username":name}, query.id == uid)
    

    print(chats.all())
    print(groupid)
    group_users = chats.search(query["id"] == groupid)[0]['users']
    if uid not in group_users:
        group_users.append(uid)
        chats.update({"users":group_users}, query.id == groupid)
        return True
    return False
    # print(type(chat))

    # us = chats.table("users")
    # if chats.search((query.users.exists()) & (query.id == update.chat.id));
        # us = chats.table("users")
    # else:
        # users.update({"users":[]}, query.id == update.chat.id)
        # us = chats.table("users")
    # us.insert(uid)
def uncountUser(bot,update,uid):
    query=Query()
    uid = str(uid)
    groupid = str(update.callback_query.message.chat.id)
    group_users = chats.search(query["id"] == groupid)[0]['users']
    if uid in group_users:
        group_users.remove(uid)
        chats.update({"users":group_users}, query.id == groupid)

def playlist(bot,update):
    chat_id = str(update.message.chat.id)
    query = Query()
    chat = chats.search(query.id == chat_id)[0]
    group_users = chat["users"]
    values=merge_users_values(group_users,chat_id)
    # for u in group_users:
        # user = users.search(query.id == u)[0]
        # for t in user["types"]:
            # if not playlist.get(t)==None:
                # playlist[t] = playlist[t]+1
            # else:
                # playlist[t] = 1
    
    # values = ""

    print(values)
    push_playlist(bot,update,parser.stream_from_values(values=values,size=10,operator="OR"))
def merge_users_values(ulist,chat_id):
    query=Query()
    # playlist = playlists[chat_id]
    playlist = {}
    print("users: "+str(ulist))
    values = ""
    for u in ulist:
        print(u)
        user = users.search(query.id == u)[0]
        user = users.search(query.id == u)[0]
        for t in user["types"]:
            if not playlist.get(t)==None:
                playlist[t] = playlist[t]+1
            else:
                playlist[t] = 1
        print("playlist"+str(playlist))
        print(user)
    for i,k in playlist.items():
        if not values == "":
            values += ","
        values+=str(i)+":"+str(int(int(k)/len(ulist)*100))
    print(values)
    return values

def push_playlist(bot,update,songs):
    bot.sendMessage(update.message.chat_id, text="Playlist")
    for s in songs:
        bot.sendAudio(update.message.chat_id, audio=open(parser.get(s['file_mp3']), 'rb'))
        

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


def empty_message(bot, update):
    """
    Empty messages could be status messages, so we check them if there is a new
    group member, someone left the chat or if the bot has been added somewhere.
    """
    print("empty_message")
    # print("The name of new member is '%s' " % update.message.new_chat_member.username)

    # Keep chatlist
    # if not chats.search(query["id"] == str(chat_id)):
        # chats.insert({"id":str(chat_id),"type":update.message.chat.type})
    # else:
        # chats.update({"type":update.message.chat.type}, query.id == str(chat_id))
    chat_id = update.message.chat.id

    if not chats.search(Query()["id"] == str(chat_id)):
        chats.insert({"id":str(chat_id),"type":update.message.chat.type})
        logger.info("I have been added to %d chats" % len(chats.all()))

    if update.message.new_chat_member is not None:
        logger.debug("The name of new member is '%s' " % update.message.new_chat_member.username)
        bot.sendMessage(chat_id=chat_id, text=update.message.new_chat_member.username)
        start(bot,update)
        # Bot was added to a group chat
        if update.message.new_chat_member.username == BOTNAME:
            return introduce(bot, update)
        # Another user joined the chat
        else:
            return welcome(bot, update)

    # Someone left the chat
    elif update.message.left_chat_member is not None:
        if update.message.left_chat_member.username != BOTNAME:
            return goodbye(bot, update)


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
