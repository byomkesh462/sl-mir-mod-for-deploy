from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram.message import Message
from telegram.update import Update
import psutil, shutil
from datetime import datetime
import time
import pytz
from bot import *
from bot.helper.ext_utils.bot_utils import get_readable_message, get_readable_file_size, get_readable_time, MirrorStatus, progress_bar, setInterval
from telegram.error import TimedOut, BadRequest


def sendMessage(text: str, bot, update: Update):
    try:
        return bot.send_message(update.message.chat_id,
                            reply_to_message_id=update.message.message_id,
                            text=text, disable_web_page_preview=True, allow_sending_without_reply=True, parse_mode='HTMl')
    except Exception as e:
        LOGGER.error(str(e))

def sendMarkup(text: str, bot, update: Update, reply_markup: InlineKeyboardMarkup):
    try:
        return bot.send_message(update.message.chat_id,
                             reply_to_message_id=update.message.message_id,
                             text=text, reply_markup=reply_markup, allow_sending_without_reply=True, parse_mode='HTMl')
    except Exception as e:
        LOGGER.error(str(e))


def sendLog(text: str, bot, update: Update, reply_markup: InlineKeyboardMarkup):
    try:
        return bot.send_message(f"{LOG_CHANNEL_ID}",
                             reply_to_message_id=update.message.message_id,
                             text=text, disable_web_page_preview=True, reply_markup=reply_markup, allow_sending_without_reply=True, parse_mode='HTMl')
    except Exception as e:
        LOGGER.error(str(e))

def sendtextlog(text: str, bot, update: Update):
    try:
        return bot.send_message(f"{LOG_SEND_TEXT}",
                             reply_to_message_id=update.message.message_id,
                             text=text, disable_web_page_preview=True, allow_sending_without_reply=True, parse_mode='HTMl')
    except Exception as e:
        LOGGER.error(str(e))


def sendPrivate(text: str, bot, update: Update, reply_markup: InlineKeyboardMarkup):
    bot_d = bot.get_me()
    b_uname = bot_d.username
    
    try:
        return bot.send_message(update.message.from_user.id,
                             reply_to_message_id=update.message.message_id,
                             text=text, disable_web_page_preview=True, reply_markup=reply_markup, allow_sending_without_reply=True, parse_mode='HTMl')
    except Exception as e:
        LOGGER.error(str(e))
        if "Forbidden" in str(e):
            uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
            botstart = f"http://t.me/{b_uname}?start=start"
            keyboard = [
            [InlineKeyboardButton("𝗦𝗧𝗔𝗥𝗧 𝗠𝗘", url = f"{botstart}")],
            [InlineKeyboardButton("𝗦𝗘𝗘 𝗟𝗢𝗚𝗦", url = f"{LOG_CHANNEL_LINK}")]]
            sendMarkup(f"𝙳𝙴𝙰𝚁 {uname},\n\n<b>⭑⭑⭑★✪ You Haven't Started Me in PM yet ✪★⭑⭑⭑</b>\n\n<b>ғʀᴏᴍ ɴᴏᴡ ᴏɴ ɪ'ʟʟ ᴤᴇɴᴅ ʟɪɴᴋᴤ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ ᴀɴᴅ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ᴏɴʟʏ</b>", bot, update, reply_markup=InlineKeyboardMarkup(keyboard))
            return


def editMessage(text: str, message: Message, reply_markup=None):
    try:
        bot.edit_message_text(text=text, message_id=message.message_id,
                              chat_id=message.chat.id,reply_markup=reply_markup,
                              parse_mode='HTMl')
    except Exception as e:
        LOGGER.error(str(e))


def deleteMessage(bot, message: Message):
    try:
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)
    except Exception as e:
        LOGGER.error(str(e))


def sendLogFile(bot, update: Update):
    with open('log.txt', 'rb') as f:
        bot.send_document(document=f, filename=f.name,
                          reply_to_message_id=update.message.message_id,
                          chat_id=update.message.chat_id)


def auto_delete_message(bot, cmd_message: Message, bot_message: Message):
    if AUTO_DELETE_MESSAGE_DURATION != -1:
        time.sleep(AUTO_DELETE_MESSAGE_DURATION)
        try:
            # Skip if None is passed meaning we don't want to delete bot xor cmd message
            deleteMessage(bot, cmd_message)
            deleteMessage(bot, bot_message)
        except AttributeError:
            pass


def delete_all_messages():
    with status_reply_dict_lock:
        for message in list(status_reply_dict.values()):
            try:
                deleteMessage(bot, message)
                del status_reply_dict[message.chat.id]
            except Exception as e:
                LOGGER.error(str(e))


def update_all_messages():
    total, used, free = shutil.disk_usage('.')
    free = get_readable_file_size(free)
    currentTime = get_readable_time(time.time() - botStartTime)
    msg, buttons = get_readable_message()
    if msg is None:
        return
    msg += f"<b>CPU:</b>{psutil.cpu_percent()}%" \
           f" <b>RAM:</b>{psutil.virtual_memory().percent}%" \
           f" <b>DISK:</b>{psutil.disk_usage('/').percent}%"
    with download_dict_lock:
        dlspeed_bytes = 0
        uldl_bytes = 0
        for download in list(download_dict.values()):
            speedy = download.speed()
            if download.status() == MirrorStatus.STATUS_DOWNLOADING:
                if 'K' in speedy:
                    dlspeed_bytes += float(speedy.split('K')[0]) * 1024
                elif 'M' in speedy:
                    dlspeed_bytes += float(speedy.split('M')[0]) * 1048576 
            if download.status() == MirrorStatus.STATUS_UPLOADING:
                if 'KB/s' in speedy:
            	    uldl_bytes += float(speedy.split('K')[0]) * 1024
                elif 'MB/s' in speedy:
                    uldl_bytes += float(speedy.split('M')[0]) * 1048576
        dlspeed = get_readable_file_size(dlspeed_bytes)
        ulspeed = get_readable_file_size(uldl_bytes)
        msg += f"\n<b>FREE:</b>{free} <b>UPTIME:</b>{currentTime}\n<b>🔻</b> <code>{dlspeed}/s</code> <b>🔺</b> <code>{ulspeed}/s</code>\n"
    with status_reply_dict_lock:
        for chat_id in list(status_reply_dict.keys()):
            if status_reply_dict[chat_id] and msg != status_reply_dict[chat_id].text:
                try:
                    if buttons == "":
                        editMessage(msg, status_reply_dict[chat_id])
                    else:
                        editMessage(msg, status_reply_dict[chat_id], buttons)
                except Exception as e:
                    LOGGER.error(str(e))
                status_reply_dict[chat_id].text = msg


def sendStatusMessage(msg, bot):
    if len(Interval) == 0:
        Interval.append(setInterval(DOWNLOAD_STATUS_UPDATE_INTERVAL, update_all_messages))
    total, used, free = shutil.disk_usage('.')
    free = get_readable_file_size(free)
    currentTime = get_readable_time(time.time() - botStartTime)
    progress, buttons = get_readable_message()
    if progress is None:
        progress, buttons = get_readable_message()
    progress += f"<b>CPU:</b> {psutil.cpu_percent()}%" \
           f" <b>RAM:</b> {psutil.virtual_memory().percent}%" \
           f" <b>DISK:</b> {psutil.disk_usage('/').percent}%"
    with download_dict_lock:
        dlspeed_bytes = 0
        uldl_bytes = 0
        for download in list(download_dict.values()):
            speedy = download.speed()
            if download.status() == MirrorStatus.STATUS_DOWNLOADING:
                if 'K' in speedy:
                    dlspeed_bytes += float(speedy.split('K')[0]) * 1024
                elif 'M' in speedy:
                    dlspeed_bytes += float(speedy.split('M')[0]) * 1048576 
            if download.status() == MirrorStatus.STATUS_UPLOADING:
                if 'KB/s' in speedy:
            	    uldl_bytes += float(speedy.split('K')[0]) * 1024
                elif 'MB/s' in speedy:
                    uldl_bytes += float(speedy.split('M')[0]) * 1048576
        dlspeed = get_readable_file_size(dlspeed_bytes)
        ulspeed = get_readable_file_size(uldl_bytes)
        progress += f"\n<b>FREE:</b> <code>{free}</code> | <b>UPTIME:</b> <code>{currentTime}</code>\n<b>DL:</b> <code>{dlspeed}/s</code> 🔻 | <b>UL:</b> <code>{ulspeed}/s</code> 🔺\n"
    with status_reply_dict_lock:
        if msg.message.chat.id in list(status_reply_dict.keys()):
            try:
                message = status_reply_dict[msg.message.chat.id]
                deleteMessage(bot, message)
                del status_reply_dict[msg.message.chat.id]
            except Exception as e:
                LOGGER.error(str(e))
                del status_reply_dict[msg.message.chat.id]
        if buttons == "":
            message = sendMessage(progress, bot, msg)
        else:
            message = sendMarkup(progress, bot, msg, buttons)
        status_reply_dict[msg.message.chat.id] = message
