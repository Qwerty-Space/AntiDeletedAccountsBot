"""See kick statistics

pattern:  `/stat(s|istics)?$`
"""

from telethon import client, events
from .global_functions import log

@events.register(events.NewMessage(pattern=r"/stat(s|istics)?$"))
async def stats(event):
    if not event.is_private:
        return

    with open("kick_counter.txt") as f:
        kick_counter = f.read()

    if not kick_counter:
        kick_counter = 0

    await event.reply(f"I have kicked a total of `{kick_counter}` deleted accounts.")
    await log(event, kick_counter)
