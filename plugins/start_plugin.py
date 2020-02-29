"""Start message

pattern: `/start$`
"""

from telethon import client, events
from .global_functions import log


# /start
@events.register(events.NewMessage(pattern=r"/start$"))
async def on_start(event):
    if event.is_private:    # If command was sent in private
        await log(event)    # Logs the event
        await event.respond('This is a bot for kicking deleted accounts from groups.  See /help for more info.')
