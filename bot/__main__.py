import shutil, psutil
import signal
import os
import asyncio
import importlib
from pyrogram import idle
from sys import executable
from pyrogram import idle, filters, types, emoji
from bot import *
from datetime import datetime
from quoters import Quote
import pytz
import time
import threading

from telegram.error import BadRequest, Unauthorized
from telegram import ParseMode, BotCommand, InputTextMessageContent, InlineQueryResultArticle, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Filters, InlineQueryHandler, MessageHandler, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.utils.helpers import escape_markdown
from telegram import ParseMode
from telegram.ext import CommandHandler
from telegraph import Telegraph
from wserver import start_server_async
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
#from bot.helper import get_text, check_heroku #---may get error
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, torrent_search, delete, speedtest, count
now=datetime.now(pytz.timezone(f'{TIMEZONE}'))

def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    current = now.strftime('%d/%m/%Y-%I:%M:%S %p')
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'╭──────┗ 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐒 ┓────\n│\n' \
            f'├─<b>⌛ BOT UPTIME:</b> <code>{currentTime}</code>\n' \
            f'├─<b>⏳ START TIME ⏳</b>───\n├─<code>{current}</code>\n' \
            f'├───<b>⚙️ ƧYƧTΣM UƧΛGΣ ⚙️</b>──\n' \
            f'├─<b>💿 Total:</b> <code>{total}</code>\n' \
            f'├─<b>📀 Used:</b> <code>{used}</code>\n' \
            f'├─<b>🕊️ Free:</b> <code>{free}</code>\n├─────────\n' \
            f'├─<b>💻 CPU:</b> <code>{cpuUsage}%</code>\n' \
            f'├─<b>🖥️ RAM:</b> <code>{memory}%</code>\n' \
            f'├─<b>💽 DISK:</b> <code>{disk}%</code>\n' \
            f'├────<b>📊 DΛTΛ USΛGΣ 📊</b>───\n├─<b>📤 Upload:</b> <code>{sent}</code>\n' \
            f'├─<b>📥 Download:</b> <code>{recv}</code>\n╰───────────────────'
    sendMessage(stats, context.bot, update)


def start(update, context):
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Repo", "https://github.com/SlamDevs/slam-mirrorbot")
    buttons.buildbutton("Channel", f"{CHANNEL_LINK}")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    LOGGER.info('UID: {} - UN: {} - MSG: {}'.format(update.message.chat.id, update.message.chat.username, update.message.text))
    uptime = get_readable_time((time.time() - botStartTime))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        if update.message.chat.type == "private" :
            sendMessage(f"Hey I'm Alive 🙂\nSince <code>{uptime}</code>", context.bot, update)
        else :
            sendMarkup(start_string, context.bot, update, reply_markup)
    else:
        sendMarkup(
            'Oops! not a Authorized user.\nPlease deploy your own <b>slam-mirrorbot</b>.',
            context.bot,
            update,
            reply_markup,
        )


def restart(update, context):
    restart_message = sendMessage("🔄️ 𝐑𝐄𝐒𝐓𝐀𝐑𝐓𝐈𝐍𝐆...", context.bot, update)
    LOGGER.info(f'Restarting The Bot...')
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    alive.terminate()
    web.terminate()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


help_string_telegraph = f'''<br>
<b>/{BotCommands.HelpCommand}</b>: To get this message
<br><br>
<b>/{BotCommands.MirrorCommand}</b> [download_url][magnet_link]: Start mirroring the link to Google Drive.
<br><br>
<b>/{BotCommands.TarMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the archived (.tar) version of the download
<br><br>
<b>/{BotCommands.ZipMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the archived (.zip) version of the download
<br><br>
<b>/{BotCommands.UnzipMirrorCommand}</b> [download_url][magnet_link]: Starts mirroring and if downloaded file is any archive, extracts it to Google Drive
<br><br>
<b>/{BotCommands.QbMirrorCommand}</b> [magnet_link]: Start Mirroring using qBittorrent, Use <b>/{BotCommands.QbMirrorCommand} s</b> to select files before downloading
<br><br>
<b>/{BotCommands.QbTarMirrorCommand}</b> [magnet_link]: Start mirroring using qBittorrent and upload the archived (.tar) version of the download
<br><br>
<b>/{BotCommands.QbZipMirrorCommand}</b> [magnet_link]: Start mirroring using qBittorrent and upload the archived (.zip) version of the download
<br><br>
<b>/{BotCommands.QbUnzipMirrorCommand}</b> [magnet_link]: Starts mirroring using qBittorrent and if downloaded file is any archive, extracts it to Google Drive
<br><br>
<b>/{BotCommands.CloneCommand}</b> [drive_url]: Copy file/folder to Google Drive
<br><br>
<b>/{BotCommands.CountCommand}</b> [drive_url]: Count file/folder of Google Drive Links
<br><br>
<b>/{BotCommands.DeleteCommand}</b> [drive_url]: Delete file from Google Drive (Only Owner & Sudo)
<br><br>
<b>/{BotCommands.WatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl. Click <b>/{BotCommands.WatchCommand}</b> for more help
<br><br>
<b>/{BotCommands.TarWatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading
<br><br>
<b>/{BotCommands.ZipWatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl and zip before uploading
<br><br>
<b>/{BotCommands.CancelMirror}</b>: Reply to the message by which the download was initiated and that download will be cancelled
<br><br>
<b>/{BotCommands.CancelAllCommand}</b>: Cancel all running tasks
<br><br>
<b>/{BotCommands.ListCommand}</b> [search term]: Searches the search term in the Google Drive, If found replies with the link
<br><br>
<b>/{BotCommands.StatusCommand}</b>: Shows a status of all the downloads
<br><br>
<b>/{BotCommands.StatsCommand}</b>: Show Stats of the machine the bot is hosted on
<br><br>
<b>/{BotCommands.UsageCommand}</b>: To see Heroku Dyno Stats (Owner & Sudo only)
'''
help = Telegraph(access_token=telegraph_token).create_page(
        title='Slam Mirrorbot Help',
        author_name='Slam Mirrorbot',
        author_url='https://github.com/SlamDevs/slam-mirrorbot',
        html_content=help_string_telegraph,
    )["path"]

help_string = f'''
/{BotCommands.PingCommand}: Check how long it takes to Ping the Bot

/{BotCommands.AuthorizeCommand}: Authorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.UnAuthorizeCommand}: Unauthorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.AuthorizedUsersCommand}: Show authorized users (Only Owner & Sudo)

/{BotCommands.AddSudoCommand}: Add sudo user (Only Owner)

/{BotCommands.RmSudoCommand}: Remove sudo users (Only Owner)

/{BotCommands.RestartCommand}: Restart the bot

/{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports

/{BotCommands.SpeedCommand}: Check Internet Speed of the Host

/{BotCommands.ShellCommand}: Run commands in Shell (Only Owner)

/{BotCommands.ExecHelpCommand}: Get help for Executor module (Only Owner)

/{BotCommands.TsHelpCommand}: Get help for Torrent search module
'''

def bot_help(update, context):
    button = button_build.ButtonMaker()
    button.buildbutton("Other Commands", f"https://telegra.ph/{help}")
    reply_markup = InlineKeyboardMarkup(button.build_menu(1))
    sendMarkup(help_string, context.bot, update, reply_markup)

'''
botcmds = [
        (f'{BotCommands.HelpCommand}','Get Detailed Help'),
        (f'{BotCommands.MirrorCommand}', 'Start Mirroring'),
        (f'{BotCommands.TarMirrorCommand}','Start mirroring and upload as .tar'),
        (f'{BotCommands.ZipMirrorCommand}','Start mirroring and upload as .zip'),
        (f'{BotCommands.UnzipMirrorCommand}','Extract files'),
        (f'{BotCommands.QbMirrorCommand}','Start Mirroring using qBittorrent'),
        (f'{BotCommands.QbTarMirrorCommand}','Start mirroring and upload as .tar using qb'),
        (f'{BotCommands.QbZipMirrorCommand}','Start mirroring and upload as .zip using qb'),
        (f'{BotCommands.QbUnzipMirrorCommand}','Extract files using qBitorrent'),
        (f'{BotCommands.CloneCommand}','Copy file/folder to Drive'),
        (f'{BotCommands.CountCommand}','Count file/folder of Drive link'),
        (f'{BotCommands.DeleteCommand}','Delete file from Drive'),
        (f'{BotCommands.WatchCommand}','Mirror Youtube-dl support link'),
        (f'{BotCommands.TarWatchCommand}','Mirror Youtube playlist link as .tar'),
        (f'{BotCommands.ZipWatchCommand}','Mirror Youtube playlist link as .zip'),
        (f'{BotCommands.CancelMirror}','Cancel a task'),
        (f'{BotCommands.CancelAllCommand}','Cancel all tasks'),
        (f'{BotCommands.ListCommand}','Searches files in Drive'),
        (f'{BotCommands.StatusCommand}','Get Mirror Status message'),
        (f'{BotCommands.StatsCommand}','Bot Usage Stats'),
        (f'{BotCommands.PingCommand}','Ping the Bot'),
        (f'{BotCommands.RestartCommand}','Restart the bot [owner/sudo only]'),
        (f'{BotCommands.UsageCommand}','See dyno [owner/sudo only]'),
        (f'{BotCommands.LogCommand}','Get the Bot Log [owner/sudo only]'),
        (f'{BotCommands.TsHelpCommand}','Get help for Torrent search module')
    ]
'''

def main():
    # Heroku restarted
    quo_te = Quote.print()
    GROUP_ID = f'{RESTARTED_GROUP_ID}'
    kie = datetime.now(pytz.timezone(f'{TIMEZONE}'))
    jam = kie.strftime('\n📅 𝘿𝘼𝙏𝙀: %d/%m/%Y\n⏲️ 𝙏𝙄𝙈𝙀: %I:%M%P')
    if GROUP_ID is not None and isinstance(GROUP_ID, str):        
        try:
            dispatcher.bot.sendMessage(f"{GROUP_ID}", f"♻️ 𝗕𝗢𝗧 𝗥𝗘𝗦𝗧𝗔𝗥𝗧𝗘𝗗 ♻️\n{jam}\n\n🗺️『𝗧𝗜𝗠𝗘 𝗭𝗢𝗡𝗘』\n{TIMEZONE}\n\n𝙿𝙻𝙴𝙰𝚂𝙴 𝚁𝙴-𝙳𝙾𝚆𝙽𝙻𝙾𝙰𝙳 𝙰𝙶𝙰𝙸𝙽\n\n𝐐𝐮𝐨𝐭𝐞\n<code>{quo_te}</code>\n\n#Restarted")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

# Heroku restarted
    GROUP_ID2 = f'{RESTARTED_GROUP_ID2}'
    kie = datetime.now(pytz.timezone(f'{TIMEZONE}'))
    jam = kie.strftime('\n📅 𝘿𝘼𝙏𝙀: %d/%m/%Y\n⏲️ 𝙏𝙄𝙈𝙀: %I:%M%P')
    if GROUP_ID2 is not None and isinstance(GROUP_ID2, str):        
        try:
            dispatcher.bot.sendMessage(f"{GROUP_ID2}", f"♻️ 𝗕𝗢𝗧 𝗥𝗘𝗦𝗧𝗔𝗥𝗧𝗘𝗗 ♻️\n{jam}\n\n🗺️『𝗧𝗜𝗠𝗘 𝗭𝗢𝗡𝗘』\n{TIMEZONE}\n\n𝙿𝙻𝙴𝙰𝚂𝙴 𝚁𝙴-𝙳𝙾𝚆𝙽𝙻𝙾𝙰𝙳 𝙰𝙶𝙰𝙸𝙽\n\n𝐐𝐮𝐨𝐭𝐞\n<code>{quo_te}</code>\n\n#Restarted")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)
            #------------------------------------------------------#
    fs_utils.start_cleanup()
    if IS_VPS:
        asyncio.get_event_loop().run_until_complete(start_server_async(PORT))
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("📶𝐑𝐄𝐒𝐓𝐀𝐑𝐓𝗘𝗗 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋𝐋𝐘...", chat_id, msg_id)
        os.remove(".restartmsg")
    elif OWNER_ID:
        try:
            text = "<b>Bot Restarted!</b>"
            bot.sendMessage(chat_id=OWNER_ID, text=text, parse_mode=ParseMode.HTML)
            if AUTHORIZED_CHATS:
                for i in AUTHORIZED_CHATS:
                    bot.sendMessage(chat_id=i, text=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            LOGGER.warning(e)
    # bot.set_my_commands(botcmds)
    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("⚠️ If Any optional vars ain't filled, it will use Defaults vars")
    LOGGER.info("📶 Bot Started!...Ready to Gooooo...")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
