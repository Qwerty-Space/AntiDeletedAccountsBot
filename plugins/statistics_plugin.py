"""Automatically kick deleted accounts

Will check periodically on new message for deleted accounts, and then kick them.
"""

from telethon import client, events
from .global_functions import log

@events.register(events.NewMessage(pattern=r"/stat(s|istics)?$"))
async def stats(event):
    if not event.is_private:
        return

    try: # Make sure the counter file doesn't already exist, otherwise create it
        with open("kick_counter.txt", "x"):
            log(event, "Kick counter file created")
    except FileExistsError:
        pass

    with open("kick_counter.txt") as f:
        kick_counter = f.read()

        await event.reply(f"I have kicked a total of `{kick_counter}` deleted accounts.")
        await log(event, {kick_counter})
