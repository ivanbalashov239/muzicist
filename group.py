#!/usr/bin/env python3
import logging

import sys
from telegram import Emoji, ParseMode, TelegramError, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, StringRegexHandler,
                          ConversationHandler, StringCommandHandler, CallbackQueryHandler, Job )
# from telegram.dispatcher import run_async
from tinydb import TinyDB, Query, operations
import traceback
import json
import config

import muzisapi

help_text = 'Welcomes everyone that enters a group chat that this bot is a ' \
            'part of. This bot can create playlist that all of you will like'

# Create database object
chats = TinyDB('chats.json')
users = TinyDB('users.json')
playlistjobs = {}

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
    bot.sendMessage(update.message.chat_id, text=help_text)


#starts the chat
def start(bot, update):
    """ Prints help text """

    print("start")
    help(bot,update)
    chat_id = update.message.chat.id

    # bot.sendMessage(chat_id=chat_id,
                    # text=help_text,
                    # parse_mode=ParseMode.MARKDOWN,
                    # disable_web_page_preview=True)
    keyboard = [[InlineKeyboardButton("connect", callback_data='connect'),InlineKeyboardButton("disconnect", callback_data='disconnect')],
            [InlineKeyboardButton("play", callback_data='play'),InlineKeyboardButton("stop", callback_data='stop')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.sendMessage(update.message.chat_id, text="Нажмите, что бы ваши предпочтения были учитаны при составлении плейлиста", reply_markup=reply_markup)

def addUser(uid,name,bot,update):
    query=Query()
    uid = str(uid)
    if update.callback_query:
        groupid = str(update.callback_query.message.chat.id)
    else:
        groupid = update.message.chat.id
    if not users.search(query["id"] == uid):
        users.insert({"id":uid,"username":name,"types":[]})
    else:
        users.update({"username":name}, query.id == uid)
    
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
def disconnect(bot,update):
    query=Query()
    if update.callback_query:
        q = update.callback_query
        qd = q.to_dict()
        uid = qd['from']['id']
        groupid = str(update.callback_query.message.chat.id)
    else:
        uid = str(update.message.left_chat_member.id)
        groupid = str(update.message.chat.id)
    group_users = chats.search(query["id"] == groupid)[0]['users']
    # if uid in group_users:
    for u in group_users:
        if str(u) == str(uid):
            group_users.remove(str(uid))
            chats.update({"users":group_users}, query.id == groupid)
            bot.sendMessage(text="@%s, вы более не учитываетесь при составлении плейлиста" % str(users.search(query.id == str(uid))[0]["username"]),
                                chat_id=groupid)
    print("disconnect")



def playlist(bot,update):
    if update.callback_query:
        chat_id = str(update.callback_query.message.chat.id)
    else:
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
    push_playlist(bot,update,parser.stream_from_values(values=values,size=5,operator="OR"))
def merge_users_values(ulist,chat_id):
    query=Query()
    # playlist = playlists[chat_id]
    playlist = {}
    print("users: "+str(ulist))
    values = ""
    for u in ulist:
        print(u)
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
    # bot.sendMessage(update.message.chat_id, text="Playlist")
    if update.callback_query:
        chat_id = str(update.callback_query.message.chat.id)
    else:
        chat_id = str(update.message.chat.id)
    for s in songs:
        bot.sendAudio(chat_id, audio=open(parser.get(s['file_mp3']), 'rb'),title=s["track_name"],performer=s["performer"],disable_notification=True)
        

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

def play(bot,update):
    if update.callback_query:
        q = update.callback_query
        qd = q.to_dict()
        uid = qd['from']['id']
        groupid = str(update.callback_query.message.chat.id)
    def callback_play(bot, job):
        print(play)
        playlist(bot,update)
        # job.schedule_removal()

    playlistjobs[groupid]=Job(callback_play,60)
    job_queue.put(playlistjobs[groupid],next_t=0.0)

    return
def stop(bot,update):
    if update.callback_query:
        q = update.callback_query
        qd = q.to_dict()
        uid = qd['from']['id']
        groupid = str(update.callback_query.message.chat.id)
    if playlistjobs.get(groupid):
        playlistjobs[groupid].schedule_removal()
    return

callback = {"connect":connect,"disconnect":disconnect,"play":play,"stop":stop}


def status_update(bot, update):
    """
    Empty messages could be status messages, so we check them if there is a new
    group member, someone left the chat or if the bot has been added somewhere.
    """
    print("status_update")
    # print("The name of new member is '%s' " % update.message.new_chat_member.username)

    # Keep chatlist
    # if not chats.search(query["id"] == str(chat_id)):
        # chats.insert({"id":str(chat_id),"type":update.message.chat.type})
    # else:
        # chats.update({"type":update.message.chat.type}, query.id == str(chat_id))
    chat_id = update.message.chat.id

    # if not chats.search(Query()["id"] == str(chat_id)):
        # chats.insert({"id":str(chat_id),"type":update.message.chat.type})
        # logger.info("I have been added to %d chats" % len(chats.all()))

    if update.message.new_chat_member is not None:
        logger.debug("The name of new member is '%s' " % update.message.new_chat_member.username)
        # Bot was added to a group chat
        if update.message.new_chat_member.username == config.BOTNAME:
            # bot.sendMessage(chat_id=chat_id, text=update.message.new_chat_member.username)
            added_to_chat(bot,update)
            start(bot,update)
            return
        # Another user joined the chat
        else:
            return

    # Someone left the chat
    elif update.message.left_chat_member is not None:
        if update.message.left_chat_member.username != config.BOTNAME:
            return disconnect(bot, update)
        else:
            removed_from_chat(bot,update)

def added_to_chat(bot,update):
    chat_id = update.message.chat.id
    query = Query()
    # playlists[str(chat_id)] = {}
    if not chats.search(query["id"] == str(chat_id)):
        chats.insert({"id":str(chat_id),"type":update.message.chat.type,"lock":True,"quiet":False,"welcome":"hi","goodbye":"bye","users":[]})
    else:
        chats.update({"id":str(chat_id),"type":update.message.chat.type,"lock":True,"quiet":False,"welcome":"hi","goodbye":"bye","users":[]}, query.id == str(chat_id))
    start(bot,update)

def removed_from_chat(bot,update):
    chats.remove(Query().id == update.message.chat_id)


def error(bot, update, error, **kwargs):
    """ Error handling """

    try:
        if isinstance(error, TelegramError)\
                and error.message == "Unauthorized"\
                or "PEER_ID_INVALID" in error.message\
                and isinstance(update, Update):
                    removed_from_chat(bot,update)
                    logger.info('Removed chat_id %s from chat list' % update.message.chat_id)
        else:
            logger.error("An error (%s) occurred: %s"
                         % (type(error), error.message))
    except:
        pass
