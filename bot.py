import re
import sys
import logging
import configparser
from os import listdir, path
from datetime import datetime
from inspect import getmembers
from plugins.global_functions import log
from importlib import import_module, reload

from telethon import TelegramClient, custom, events, sync
from telethon.tl.types import (MessageEntityTextUrl, MessageEntityUrl,
                               MessageMediaDocument, MessageMediaPhoto)

logging.basicConfig(level=logging.INFO)
sys.dont_write_bytecode = True


### VARIABLES ###
config = configparser.ConfigParser()
config.read_file(open("config.ini"))
token = config['DEFAULT']['TOKEN']
session_name = config['DEFAULT']['SESSION_NAME']
api_id = config['DEFAULT']['ID']
api_hash = config['DEFAULT']['HASH']
superadmin = int(config['DEFAULT']['SUPERADMIN'])
script_dir = path.dirname(path.realpath(__file__))  # Set the location of the script


### LOG IN TO TELEGRAM ##
client = TelegramClient(path.join(script_dir, session_name), api_id, api_hash)


### IMPORT PLUGINS ###
plugindir = "plugins" # Change plugin path here
pluginfiles = listdir(plugindir)
plugin_dict = {}

for pluginfile in pluginfiles:
    if re.search(r".+plugin\.py$", pluginfile):
        plugin_name = pluginfile[:-3]
        plugin_shortname = plugin_name[:-7]
        plugin = import_module(f"plugins.{plugin_name}")
        plugin_dict[plugin_shortname] = plugin.__doc__
        for name, handler in getmembers(plugin):
            if events.is_handler(handler):
                client.add_event_handler(handler)


# ## RELOAD PLUGINS ###
# @client.on(events.NewMessage(pattern=r"^/reload$"))
# async def reload_plugins(event):
#     for name, module in sys.modules.items():
#         print(name)
#         print(module)
#         reload(module)


### HELP! ###
plugin_list = "`\n• `".join(plugin_dict)
help_message = f"""**List of functions:**
• `{plugin_list}`

Do `/help <command>` to learn more about it.
"""


try: # Make sure the counter file doesn't already exist, otherwise create it
    with open("kick_counter.txt", "x"):
        logging.info("Kick counter file created")
except FileExistsError:
    pass


@client.on(events.NewMessage(pattern=r"^/help(?: (\S+))?$"))
async def help(event):
    if event.is_private:
        await log(event)
        try:
            await event.respond(plugin_dict[event.pattern_match.group(1)], link_preview=False)
        except:
            await event.respond(help_message, link_preview=False)


try:
    client.start(bot_token=token)
except KeyboardInterrupt:
    sys.exit()
try:
    client.send_message(superadmin, f"**Bot started at:**  {datetime.now().strftime('`%c`')}")
except ValueError:
    pass

print(f"Bot started at:  {datetime.now().strftime('%c')}")
client.run_until_disconnected()
