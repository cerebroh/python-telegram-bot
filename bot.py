#!/usr/bin/env python
# -*- coding: utf-8 -*-

#python_telegram_bot

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.error import TelegramError, BadRequest
import telegram, logging
from threading import Thread
import os, sys, time, datetime, json, random, re, requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables
bot_token = "691091364:AAHEJZdJnx5mHXbPTSS6x0Xgxa9Jl8jC3QE"
data_folder = ""
tumblr_db_file = data_folder + "tumblr_db.json"
nsfw_bot_id = 691091364
nsfw_bot_gr = -1001022046952
nsfw_bot_pvt =  -1001229855326
bot_spam_channel = -1001356151287
nsfw_admins = [127396236, 381322992, 27588466, 28752541]

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def error(bot, update, error):
    """Log Errors caused by Updates."""
    if str(error) != "Timed out":
        bot.send_message(bot_spam_channel, str(error))
    logger.warning('Update "%s" caused error "%s"', update, error)

# Return (chatid, messageid, ischannel): fromchatid, messageid, ch = handleupdate(update)
def handleupdate(update):
    try:
        fromchatid = update.message.chat.id
        messageid = update.message.message_id
    except AttributeError:
        try:
            fromchatid = update.channel_post.chat.id
            messageid = update.channel_post.message_id
            ch = True
        except:
            return False, False, False
        return fromchatid, messageid, ch
    except:
        return False, False, False
    ch = False
    return fromchatid, messageid, ch

# def get_invite_link():
    # with open(users_db_file, 'r') as users_db:
        # users_lists = json.load(users_db)
    # invitelink = users_lists["invitelink"]
    # return invitelink

def get_subs(sub):
    with open(tumblr_db_file, 'r') as tumblr_db:
        tumblr_list = json.load(tumblr_db)
    subs = tumblr_list[sub]
    return subs

def get_active_subs():
    with open(tumblr_db_file, 'r') as tumblr_db:
        tumblr_list = json.load(tumblr_db)
    active_subs = tumblr_list["active"]
    return active_subs

def start_sub(sub):
    with open(tumblr_db_file, 'r+') as tumblr_db:
        tumblr_list = json.load(tumblr_db)
        active_subs = tumblr_list["active"]
        active_subs.append(sub)
        tumblr_db.seek(0)
        tumblr_db.truncate()
        json.dump(tumblr_list, tumblr_db, sort_keys = True, indent = 4)

def stop_sub(sub):
    with open(tumblr_db_file, 'r+') as tumblr_db:
        tumblr_list = json.load(tumblr_db)
        active_subs = tumblr_list["active"]
        active_subs.remove(sub)
        tumblr_db.seek(0)
        tumblr_db.truncate()
        json.dump(tumblr_list, tumblr_db, sort_keys = True, indent = 4)

def get_tumblr_tag_info(tumblr_name, tumblr_tag):
    url = "https://api.tumblr.com/v2/blog/" + tumblr_name + ".tumblr.com/posts?api_key=AbEXWryGJqKYUHeCmnqo1eOttY18M1LmBuKsU93HsqK16JAP2X&tag=" + tumblr_tag + "&limit=1"
    try:
        response = requests.get(url)
        tumblr_tag_info = response.json()
    except:
        return False
    return tumblr_tag_info

def get_tumblr_info(tumblr_name):
    url = "https://api.tumblr.com/v2/blog/" + tumblr_name + ".tumblr.com/info?api_key=AbEXWryGJqKYUHeCmnqo1eOttY18M1LmBuKsU93HsqK16JAP2X"
    try:
        response = requests.get(url)
        tumblr_info = response.json()
    except:
        return False
    return tumblr_info

def get_tumblr_posts(tumblr_name, tumblr_tag, tumblr_post_off, limit):
    if tumblr_tag == "":
        url = "https://api.tumblr.com/v2/blog/" + tumblr_name + ".tumblr.com/posts?api_key=AbEXWryGJqKYUHeCmnqo1eOttY18M1LmBuKsU93HsqK16JAP2X&offset=" + str(tumblr_post_off) + "&limit=" + limit
    else:
        url = "https://api.tumblr.com/v2/blog/" + tumblr_name + ".tumblr.com/posts?api_key=AbEXWryGJqKYUHeCmnqo1eOttY18M1LmBuKsU93HsqK16JAP2X&tag=" + tumblr_tag + "&offset=" + str(tumblr_post_off) + "&limit=" + limit
    try:
        response = requests.get(url)
        tumblr_posts = response.json()
    except:
        return False
    return tumblr_posts

def gif_check(url):
    url_chunks = url.split("/")
    ext = url_chunks[-1][-4:]
    if ext == ".gif":
        return True
    else:
        return False

def get_tumblrs(sub):
    with open(tumblr_db_file, 'r') as tumblr_db:
        tumblr_list = json.load(tumblr_db)
    tumblrs = tumblr_list[str(sub)]
    return tumblrs

def update_tumblr_list(sub, tumblr_name, tumblr_tag, tumblr_post_tot, tumblr_post_off):
    with open(tumblr_db_file, 'r+') as tumblr_db:
        tumblr_list = json.load(tumblr_db)
        for tumblr in tumblr_list[str(sub)]:
            if tumblr["name"] == tumblr_name and tumblr["tag"] == tumblr_tag:
                tumblr["tot"] = tumblr_post_tot
                tumblr["off"] = tumblr_post_off
        tumblr_db.seek(0)
        tumblr_db.truncate()
        json.dump(tumblr_list, tumblr_db, sort_keys = True, indent = 4)
    return True

def vote_handler(bot, update):
    cqd = update.callback_query.data
    if cqd == "👍":
        if update.callback_query.message.document:
            bot.sendDocument(chat_id=nsfw_bot_gr, document=update.callback_query.message.document.file_id)
        elif update.callback_query.message.photo:
            bot.sendPhoto(chat_id=nsfw_bot_gr, photo=update.callback_query.message.photo[-1].file_id)
        bot.delete_message(update.callback_query.message.chat.id, update.callback_query.message.message_id)
        return
    elif cqd == "👎" and update.callback_query.message.chat.id == nsfw_bot_pvt:
        bot.delete_message(update.callback_query.message.chat.id, update.callback_query.message.message_id)
        return

def postDocument(bot, job):
    # context = {"sub": sub, "url": url}
    sub = job.context["sub"]
    url = job.context["url"]
    vote_buttons = [
        telegram.InlineKeyboardButton(text="👍", callback_data="👍"),
        telegram.InlineKeyboardButton(text="👎", callback_data="👎")
    ]
    try:
        reply_markup = telegram.InlineKeyboardMarkup([vote_buttons])
        bot.sendDocument(sub, url, reply_markup=reply_markup)
        
    except:
        bot.sendMessage(bot_spam_channel, "Something went wrong while sending document from {} to {}".format(url, sub))
        return

def postPhoto(bot, job):
    # context = {"sub": sub, "url": url}
    sub = job.context["sub"]
    url = job.context["url"]
    vote_buttons = [
        telegram.InlineKeyboardButton(text="👍", callback_data="👍"),
        telegram.InlineKeyboardButton(text="👎", callback_data="👎")
    ]
    try:
        reply_markup = telegram.InlineKeyboardMarkup([vote_buttons])
        bot.sendPhoto(sub, url, reply_markup=reply_markup)
    except:
        bot.sendMessage(bot_spam_channel, "Something went wrong while sending photo from {} to {}".format(url, sub))
        return

def postMessageDone(bot, job):
    # context = {"sub": sub, "url": url}
    sub = job.context["sub"]
    try:
        bot.sendMessage(sub, "Done!")
    except:
        bot.sendMessage(bot_spam_channel, "Something went wrong while sending done message to {}".format(sub))
        return

def postMessageCheck(bot, job):
    # context = {"sub": sub, "tmblr":tumblr_name}
    sub = job.context["sub"]
    tmblr = job.context["tmblr"]
    try:
        bot.sendMessage(sub, "Checking http://{}".format(tmblr))
    except:
        bot.sendMessage(bot_spam_channel, "Something went wrong while sending check message to {}".format(sub))
        return

def start(bot, update):
    bot.send_chat_action(update.message.chat.id, action='TYPING')
    if update.message.from_user.id in nsfw_admins:
        update.message.reply_text('Type "link" to get our invite link.\nType ".help" to get subscription commands.')
    else:
        update.message.reply_text('Type "link" to get our invite link.')

def checkcommands(bot, update, job_queue, chat_data):
    fromchatid, messageid, ch = handleupdate(update)
    if fromchatid == nsfw_bot_pvt:
        sub = nsfw_bot_pvt
    elif fromchatid in nsfw_admins:
        sub = fromchatid
    else:
        return
    if update.message.text.startswith(".check ") and update.message.text != ".check":
        bot.send_chat_action(update.message.chat.id, action='TYPING')
        arguments = update.message.text[7:]
        try:
            if arguments.startswith("http://") or arguments.startswith("https://"):
                arguments = arguments.split("//")
                if "/tagged/" in arguments[1]:
                    arguments = arguments[1].split("/tagged/")
                    tumblr_name = arguments[0]
                    tumblr_name = tumblr_name.replace(".tumblr.com", "")
                    tumblr_tag = arguments[1]
                    tumblr_tag = tumblr_tag.replace("#", "")
                    tumblr_tag = tumblr_tag.replace("/", "")
                    tumblr_tag = tumblr_tag.replace(" ", "+")
                    tumblr_tag = tumblr_tag.replace("%20", "+")
                else:
                    tumblr_name = arguments[1]
                    tumblr_name = tumblr_name.replace(".tumblr.com", "")
                    tumblr_name = tumblr_name.replace("/", "")
                    tumblr_tag = ""
            else:
                arguments = arguments.split()
                if len(arguments) > 1:
                    tumblr_name = arguments[0]
                    i = 2
                    tumblr_tag = arguments[1]
                    while i < len(arguments):
                        tumblr_tag = tumblr_tag + "+" + arguments[i]
                        i += 1
                    tumblr_tag = tumblr_tag.replace("#", "")
                    tumblr_tag = tumblr_tag.replace("%20", "+")
                else:
                    tumblr_name = arguments[0]
                    tumblr_tag = ""
        except:
            update.message.reply_text("Can't recognize this url: {}\nMake sure it's in one of these formats:\nhttp://tumblr_name.tumblr.com/\nhttp://tumblr_name.tumblr.com/tagged/tag\ntumblr_name tag".format(update.message.text[7:]))
            return
        update.message.reply_text("Checking...")
        # get last 10 posts
        tumblr_posts = get_tumblr_posts(tumblr_name, tumblr_tag, tumblr_post_off=0, limit="10")
        if tumblr_posts == False:
            update.message.reply_text("Something went wrong connecting with http://{}.tumblr.com/".format(tumblr_name))
            return
        time = 5
        for i in range(len(tumblr_posts["response"]["posts"])):
            if tumblr_posts["response"]["posts"][i]["type"] == "photo":
                photos = tumblr_posts["response"]["posts"][i]["photos"]
                for photo in photos:
                    url = photo["original_size"]["url"]
                    gif = gif_check(url)
                    if gif:
                        job_queue.run_once(postDocument, time, context={"sub": sub, "url": url})
                        time += 5
                    else:
                        job_queue.run_once(postPhoto, time, context={"sub": sub, "url": url})
                        time += 5
            # elif tumblr_posts["response"]["posts"][i]["type"] == "video":
                # try:
                    # url = tumblr_posts["response"]["posts"][i]["video_url"]
                # except:
                    # continue
                # try:
                    # job_queue.run_once(postDocument, time, context={"sub": sub, "url": url})
                    # time += 5
                # except:
                    # continue
            else:
                continue
        time += 5
        job_queue.run_once(postMessageDone, time, context={"sub":sub})
        # check done
    elif update.message.text == ".check":
        bot.send_chat_action(update.message.chat.id, action='TYPING')
        try:
            tumblrs = get_tumblrs(sub)
        except KeyError:
            update.message.reply_text("You have no active subscriptions.")
            return
        time = 5
        for tumblr in tumblrs:
            tumblr_name = tumblr["name"]
            tumblr_post_tot = tumblr["tot"]
            tumblr_post_off = tumblr["off"]
            tumblr_tag = tumblr["tag"]
            if tumblr_tag != "":
                # check its info
                tumblr_tag_info = get_tumblr_tag_info(tumblr_name, tumblr_tag)
                if tumblr_tag_info == False:
                    bot.send_message(sub, "Something went wrong connecting with http://{}.tumblr.com/tagged/{}".format(tumblr_name, tumblr_tag))
                    continue
                # check if new posts
                if tumblr_tag_info["response"]["total_posts"] > tumblr_post_tot:
                    diff = tumblr_tag_info["response"]["total_posts"] - tumblr_post_tot
                    tumblr_post_tot = tumblr_tag_info["response"]["total_posts"]
                    tumblr_post_off = tumblr_post_off + diff
                if tumblr_post_off < 0:
                    tumblr_post_off = 0
                # check if there's something to post
                if tumblr_post_off == 0:
                    bot.send_message(sub, "{} - #{} has no new posts".format(tumblr_name, tumblr_tag))
                    continue
                else:
                    # there's stuff to post!
                    job_queue.run_once(postMessageCheck, time, context={"sub":sub, "tmblr":(tumblr_name + "tumblr.com/tagged/" + tumblr_tag)})
                    time += 5
            else:
                # check its info
                tumblr_info = get_tumblr_info(tumblr_name)
                if tumblr_info == False:
                    bot.send_message(sub, "Something went wrong connecting with http://{}.tumblr.com/".format(tumblr_name))
                    continue
                # check if new posts
                if tumblr_info["response"]["blog"]["posts"] > tumblr_post_tot:
                    diff = tumblr_info["response"]["blog"]["posts"] - tumblr_post_tot
                    tumblr_post_tot = tumblr_info["response"]["blog"]["posts"]
                    tumblr_post_off = tumblr_post_off + diff
                    if tumblr_post_off < 0:
                        tumblr_post_off = 0
                # check if there's something to post
                if tumblr_post_off == 0:
                    bot.send_message(sub, "{} has no new posts".format(tumblr_name))
                    continue
                else:
                    # there's stuff to post!
                    job_queue.run_once(postMessageCheck, time, context={"sub":sub, "tmblr":(tumblr_name + "tumblr.com")})
                    time += 5
            # get 20 posts
            if tumblr_post_off < 20:
                limit = str(tumblr_post_off)
                tumblr_post_offset = 0
            else:
                limit = "20"
                tumblr_post_offset = tumblr_post_off - 20
            tumblr_posts = get_tumblr_posts(tumblr_name, tumblr_tag, tumblr_post_offset, limit)
            if tumblr_posts == False:
                update.message.reply_text("Something went wrong connecting with http://{}.tumblr.com/".format(tumblr_name))
                return
            resplen = len(tumblr_posts["response"]["posts"]) - 1
            for i in range(len(tumblr_posts["response"]["posts"])):
                if tumblr_posts["response"]["posts"][resplen - i]["type"] == "photo":
                    photos = tumblr_posts["response"]["posts"][resplen - i]["photos"]
                    for photo in photos:
                        url = photo["original_size"]["url"]
                        gif = gif_check(url)
                        if gif:
                            job_queue.run_once(postDocument, time, context={"sub": sub, "url": url})
                            time += 5
                        else:
                            job_queue.run_once(postPhoto, time, context={"sub": sub, "url": url})
                            time += 5
                # elif tumblr_posts["response"]["posts"][resplen - i]["type"] == "video":
                    # try:
                        # url = tumblr_posts["response"]["posts"][resplen - i]["video_url"]
                    # except:
                        # continue
                    # try:
                        # job_queue.run_once(postDocument, time, context={"sub": sub, "url": url})
                        # time += 5
                    # except:
                        # continue
                else:
                    continue
            if i < resplen:
                tumblr_post_off -= (i + 1)
            else:
                tumblr_post_off -= i
            # save to db
            update_tumblr_list(sub, tumblr_name, tumblr_tag, tumblr_post_tot, tumblr_post_off)
            # tumblr done
        time += 5
        job_queue.run_once(postMessageDone, time, context={"sub":sub})
        # check done
    elif update.message.text.startswith(".add ") and update.message.text != ".add":
        bot.send_chat_action(update.message.chat.id, action='TYPING')
        arguments = update.message.text[5:]
        try:
            if arguments.startswith("http://") or arguments.startswith("https://"):
                arguments = arguments.split("//")
                if "/tagged/" in arguments[1]:
                    arguments = arguments[1].split("/tagged/")
                    tumblr_name = arguments[0]
                    tumblr_name = tumblr_name.replace(".tumblr.com", "")
                    tumblr_tag = arguments[1]
                    tumblr_tag = tumblr_tag.replace("#", "")
                    tumblr_tag = tumblr_tag.replace("/", "")
                    tumblr_tag = tumblr_tag.replace(" ", "+")
                    tumblr_tag = tumblr_tag.replace("%20", "+")
                else:
                    tumblr_name = arguments[1]
                    tumblr_name = tumblr_name.replace(".tumblr.com", "")
                    tumblr_name = tumblr_name.replace("/", "")
                    tumblr_tag = ""
            else:
                arguments = arguments.split()
                if len(arguments) > 1:
                    tumblr_name = arguments[0]
                    i = 2
                    tumblr_tag = arguments[1]
                    while i < len(arguments):
                        tumblr_tag = tumblr_tag + "+" + arguments[i]
                        i += 1
                    tumblr_tag = tumblr_tag.replace("#", "")
                    tumblr_tag = tumblr_tag.replace("%20", "+")
                else:
                    tumblr_name = arguments[0]
                    tumblr_tag = ""
        except:
            update.message.reply_text("Can't recognize this url: {}\nMake sure it's in one of these formats:\nhttp://tumblr_name.tumblr.com/\nhttp://tumblr_name.tumblr.com/tagged/tag\ntumblr_name tag".format(update.message.text[5:]))
            return
        if tumblr_tag != "":
            tumblr_info = get_tumblr_tag_info(tumblr_name, tumblr_tag)
            if tumblr_info == False:
                    update.message.reply_text("Something went wrong connecting with http://{}.tumblr.com/tagged/{}".format(tumblr_name, tumblr_tag))
                    return
            tumblr_tot = tumblr_info["response"]["total_posts"]
        else:
            tumblr_info = get_tumblr_info(tumblr_name)
            if tumblr_info == False:
                    update.message.reply_text("Something went wrong connecting with http://{}.tumblr.com/".format(tumblr_name))
                    return
            tumblr_tot = tumblr_info["response"]["blog"]["posts"]
        with open(tumblr_db_file, 'r+') as tumblr_db:
            tumblr_list = json.load(tumblr_db)
            newtumblr = {"name": tumblr_name, "tag": tumblr_tag, "tot": tumblr_tot, "off": tumblr_tot}
            try:
                sub_list = tumblr_list[str(sub)]
                for sub_data in sub_list:
                    if sub_data["name"] == tumblr_name:
                        if sub_data["tag"] == "":
                            update.message.reply_text("Already subscribed to all posts from {}".format(tumblr_name))
                            return
                        elif sub_data["tag"] == tumblr_tag:
                            update.message.reply_text("Already subscribed to #{} from {}".format(tumblr_tag, tumblr_name))
                            return
            except KeyError:
                tumblr_list[str(sub)] = []
                start_sub(sub)
            tumblr_list[str(sub)].append(newtumblr)
            tumblr_db.seek(0)
            tumblr_db.truncate()
            json.dump(tumblr_list, tumblr_db, sort_keys = True, indent = 4)
        update.message.reply_text("Added to subscriptions.")
    elif update.message.text.startswith(".del ") and update.message.text != ".del":
        bot.send_chat_action(update.message.chat.id, action='TYPING')
        arguments = update.message.text[5:]
        try:
            if arguments.startswith("http://") or arguments.startswith("https://"):
                arguments = arguments.split("//")
                if "/tagged/" in arguments[1]:
                    arguments = arguments[1].split("/tagged/")
                    tumblr_name = arguments[0]
                    tumblr_name = tumblr_name.replace(".tumblr.com", "")
                    tumblr_tag = arguments[1]
                    tumblr_tag = tumblr_tag.replace("#", "")
                    tumblr_tag = tumblr_tag.replace("/", "")
                    tumblr_tag = tumblr_tag.replace(" ", "+")
                    tumblr_tag = tumblr_tag.replace("%20", "+")
                else:
                    tumblr_name = arguments[1]
                    tumblr_name = tumblr_name.replace(".tumblr.com", "")
                    tumblr_name = tumblr_name.replace("/", "")
                    tumblr_tag = ""
            else:
                arguments = arguments.split()
                if len(arguments) > 1:
                    tumblr_name = arguments[0]
                    i = 2
                    tumblr_tag = arguments[1]
                    while i < len(arguments):
                        tumblr_tag = tumblr_tag + "+" + arguments[i]
                        i += 1
                    tumblr_tag = tumblr_tag.replace("#", "")
                    tumblr_tag = tumblr_tag.replace("%20", "+")
                else:
                    tumblr_name = arguments[0]
                    tumblr_tag = ""
        except:
            update.message.reply_text("Can't recognize this url: {}\nMake sure it's in one of these formats:\nhttp://tumblr_name.tumblr.com/\nhttp://tumblr_name.tumblr.com/tagged/tag\ntumblr_name tag".format(update.message.text[5:]))
            return
        with open(tumblr_db_file, 'r+') as tumblr_db:
            tumblr_list = json.load(tumblr_db)
            try:
                sub_list = tumblr_list[str(sub)]
            except KeyError:
                update.message.reply_text("No subscription to be removed found. Use .sub to check your subscriptions.")
                return
            data_to_remove = False
            for sub_data in sub_list:
                if sub_data["name"] == tumblr_name and sub_data["tag"] == tumblr_tag:
                    data_to_remove = sub_data
                    break
            if data_to_remove == False:
                update.message.reply_text("No subscription to be removed found. Use .sub to check your subscriptions.")
                return
            tumblr_list[str(sub)].remove(data_to_remove)
            if len(tumblr_list[str(sub)]) == 0:
                stop_sub(sub)
            tumblr_db.seek(0)
            tumblr_db.truncate()
            json.dump(tumblr_list, tumblr_db, sort_keys = True, indent = 4)
        update.message.reply_text("Deleted from subscriptions.")
    elif update.message.text == ".sub":
        bot.send_chat_action(update.message.chat.id, action='TYPING')
        try:
            subs = get_subs(str(sub))
        except KeyError:
            update.message.reply_text("You have no active subscriptions.")
            return
        if len(subs) == 0:
            replymsg = "No subscriptions."
        else:
            if sub == nsfw_bot_pvt:
                replymsg = "Subscriptions for the group:\n"
            else:
                replymsg = "Your subscriptions:"
            for sub_data in subs:
                replymsg = replymsg + "\n\nhttp://" + sub_data["name"] + ".tumblr.com"
                if sub_data["tag"] != "":
                    replymsg = replymsg + "/tagged/" + sub_data["tag"]
                replymsg = replymsg + "\n" + str(sub_data["tot"] - 1) + " total posts, " + str(sub_data["off"]) + " to be posted."
        if len(replymsg) < 4095:
            update.message.reply_text(replymsg)
        else:
            replymsgs = [replymsg[i:i+4095] for i in range(0, len(replymsg), 4095)]
            for replymsg in replymsgs:
                update.message.reply_text(replymsg)
    elif update.message.text == ".start":
        bot.send_chat_action(update.message.chat.id, action='TYPING')
        active_subs = get_active_subs()
        if sub not in active_subs:
            start_sub(sub)
            update.message.reply_text("Automatic posts enabled.")
        else:
            update.message.reply_text("Automatic posts are already enabled.")
    elif update.message.text == ".stop":
        bot.send_chat_action(update.message.chat.id, action='TYPING')
        active_subs = get_active_subs()
        if sub in active_subs:
            stop_sub(sub)
            update.message.reply_text("Automatic posts disabled.")
        else:
            update.message.reply_text("Automatic posts are already disabled.")
    elif update.message.text == ".help":
        bot.send_chat_action(update.message.chat.id, action='TYPING')
        update.message.reply_text('.add URL / .add TUMBLR_NAME (#TAG): add a tumblr to subscription, if no tag is present will check every post.\n  ".add italiansd0itbetter"\n  ".add italiansd0itbetter #from behind"\n  ".add http://italiansd0itbetter.tumblr.com/tagged/from+behind"\n\n.del URL / .del TUMBLR_NAME (#TAG): delete a tumblr from subscription.\n  ".del italiansd0itbetter"\n  ".del italiansd0itbetter #from behind"\n  ".del http://italiansd0itbetter.tumblr.com/tagged/from+behind"\n\n.sub: lists all subscriptions.\n\n.start: enable automatic posts\n\n.stop: disable automatic posts\n\n.check: without arguments, check if all subscriptions have new posts.\n\n.check URL / .check TUMBLR_NAME (#TAG): check last 10 posts from the tumblr, even if not subscribed.\n  ".check italiansd0itbetter"\n  ".check italiansd0itbetter #from behind"\n  ".check http://italiansd0itbetter.tumblr.com/tagged/from+behind"')
    else:
        return

def checkmention(bot, update):
    if update.message.from_user.id in nsfw_admins:
        return
    entities = re.findall("(@[\w_]+)", update.message.text)
    for entity in entities:
        if entity.endswith("bot"):
            bot.delete_message(update.message.chat.id, update.message.message_id)
            return
        try:
            chat_info = bot.get_chat(entity)
            if chat_info.id < 0:
                bot.delete_message(update.message.chat.id, update.message.message_id)
                return
        except:
            continue

def checklink(bot, update):
    fromchatid, messageid, ch = handleupdate(update)
    bot.send_chat_action(fromchatid, action='TYPING')
    # invitelink = get_invite_link()
    update.message.reply_text("https://t.me/joinchat/B5fpjDzrMug-mYTMiw0-nA")

def renew(bot, update):
    newlink = bot.export_chat_invite_link(update.message.chat.id)
    update.message.reply_text(newlink)

def start_queueing(updater):
    postinterval = datetime.timedelta(hours = 5)
    dt = datetime.datetime.now()
    firstinterval = dt + datetime.timedelta(minutes = 5)
    j = updater.job_queue
    job_autoPost = j.run_repeating(autoPost, interval=postinterval, first=firstinterval, context=j, name="queuePosts")
    
def autoPost(bot, job):
    sub = nsfw_bot_pvt
    subs = get_active_subs()
    if sub not in subs:
        bot.send_message(sub, "Subscriptions for nsfw private group are disabled.")
        return
    try:
        tumblrs = get_tumblrs(sub)
    except KeyError:
        bot.send_message(sub, "No subscriptions for nsfw private group are active.")
        return
    job_autoQueue = job.context
    time = 5
    for tumblr in tumblrs:
        tumblr_name = tumblr["name"]
        tumblr_post_tot = tumblr["tot"]
        tumblr_post_off = tumblr["off"]
        tumblr_tag = tumblr["tag"]
        if tumblr_tag != "":
            # check its info
            tumblr_tag_info = get_tumblr_tag_info(tumblr_name, tumblr_tag)
            if tumblr_tag_info == False:
                bot.send_message(sub, "Something went wrong connecting with http://{}.tumblr.com/tagged/{}".format(tumblr_name, tumblr_tag))
                continue
            # check if new posts
            if tumblr_tag_info["response"]["total_posts"] > tumblr_post_tot:
                diff = tumblr_tag_info["response"]["total_posts"] - tumblr_post_tot
                tumblr_post_tot = tumblr_tag_info["response"]["total_posts"]
                tumblr_post_off = tumblr_post_off + diff
            if tumblr_post_off < 0:
                tumblr_post_off = 0
            # check if there's something to post
            if tumblr_post_off == 0:
                bot.send_message(sub, "{} - #{} has no new posts".format(tumblr_name, tumblr_tag))
                continue
            else:
                # there's stuff to post!
                job_autoQueue.run_once(postMessageCheck, time, context={"sub":sub, "tmblr":(tumblr_name + "tumblr.com/tagged/" + tumblr_tag)})
                time += 5
        else:
            # check its info
            tumblr_info = get_tumblr_info(tumblr_name)
            if tumblr_info == False:
                bot.send_message(sub, "Something went wrong connecting with http://{}.tumblr.com/".format(tumblr_name))
                continue
            # check if new posts
            if tumblr_info["response"]["blog"]["posts"] > tumblr_post_tot:
                diff = tumblr_info["response"]["blog"]["posts"] - tumblr_post_tot
                tumblr_post_tot = tumblr_info["response"]["blog"]["posts"]
                tumblr_post_off = tumblr_post_off + diff
                if tumblr_post_off < 0:
                    tumblr_post_off = 0
            # check if there's something to post
            if tumblr_post_off == 0:
                bot.send_message(sub, "{} has no new posts".format(tumblr_name))
                continue
            else:
                # there's stuff to post!
                job_autoQueue.run_once(postMessageCheck, time, context={"sub":sub, "tmblr":(tumblr_name + "tumblr.com")})
                time += 5
        # get 20 posts
        if tumblr_post_off < 20:
            limit = str(tumblr_post_off)
            tumblr_post_offset = 0
        else:
            limit = "20"
            tumblr_post_offset = tumblr_post_off - 20
        tumblr_posts = get_tumblr_posts(tumblr_name, tumblr_tag, tumblr_post_offset, limit)
        if tumblr_posts == False:
            bot.send_message(sub, "Something went wrong connecting with http://{}.tumblr.com/".format(tumblr_name))
            return
        resplen = len(tumblr_posts["response"]["posts"]) - 1
        for i in range(len(tumblr_posts["response"]["posts"])):
            if tumblr_posts["response"]["posts"][resplen - i]["type"] == "photo":
                photos = tumblr_posts["response"]["posts"][resplen - i]["photos"]
                for photo in photos:
                    url = photo["original_size"]["url"]
                    gif = gif_check(url)
                    if gif:
                        job_autoQueue.run_once(postDocument, time, context={"sub": sub, "url": url})
                        time += 5
                    else:
                        job_autoQueue.run_once(postPhoto, time, context={"sub": sub, "url": url})
                        time += 5
            # elif tumblr_posts["response"]["posts"][resplen - i]["type"] == "video":
                # try:
                    # url = tumblr_posts["response"]["posts"][resplen - i]["video_url"]
                # except:
                    # continue
                # try:
                    # job_autoQueue.run_once(postDocument, time, context={"sub": sub, "url": url})
                    # time += 5
                # except:
                    # continue
            else:
                continue
        if i < resplen:
            tumblr_post_off -= (i + 1)
        else:
            tumblr_post_off -= i
        # save to db
        update_tumblr_list(sub, tumblr_name, tumblr_tag, tumblr_post_tot, tumblr_post_off)
        # tumblr done
    time += 5
    job_autoQueue.run_once(postMessageDone, time, context={"sub":sub})
    # check done

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)
    
    def restart(bot, update):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()    
    
    def stopbot(bot, update):
        """Gracefully stop the Updater"""
        update.message.reply_text('Bot is shutting down...')
        updater.stop()
    
    def uptime(bot, update):
        strttm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(starttime))
        uptm = time.time() - starttime
        m, s = divmod(uptm, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        update.message.reply_text("Uptime: {:d}days {:02d}h {:02d}m {:05.2f}s - since {}".format(int(d), int(h), int(m), s, strttm))
    
    # on different commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("uptime", uptime, filters=Filters.user(127396236)))
    dp.add_handler(CommandHandler("restart", restart, filters=Filters.user(127396236)))
    dp.add_handler(CommandHandler("stop", stopbot, filters=Filters.user(127396236)))
    dp.add_handler(CommandHandler("renew", renew, filters=Filters.user(127396236)))
    dp.add_handler(telegram.ext.CallbackQueryHandler(vote_handler))
    
    # on noncommand i.e message
    # text messages to any chat not (nsfw_bot_gr), starting with "."
    dp.add_handler(MessageHandler(((~ Filters.chat(chat_id=nsfw_bot_gr)) & Filters.text & Filters.regex('^\.')), checkcommands, pass_job_queue=True, pass_chat_data=True))
    # messages to (nsfw_bot_gr) containing mentions
    dp.add_handler(MessageHandler((Filters.entity("mention") & Filters.chat(chat_id=nsfw_bot_gr)), checkmention))
    # "!link", "link", "link?"
    dp.add_handler(MessageHandler((Filters.text & Filters.regex('^!?[lL][iI][nN][kK]\??$')), checklink))
    
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    print ("NSFW bot online")
    updater.bot.send_message(bot_spam_channel, "NSFW bot online")
    start_queueing(updater)
    starttime = time.time()
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
