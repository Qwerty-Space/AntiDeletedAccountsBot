"""See kick statistics
"""

from telethon import client, events, sessions, errors
from .global_functions import log, cooldown
from asyncio import sleep
import sqlite3


@events.register(events.NewMessage())
@cooldown(60 * 60 * 60, False) # Only activate at minimum once an hour
async def kick_deleted(event):
    if not event.is_group:
        return

    group = await event.get_chat() # Get group object
    kicked_users = 0

    async for user in event.client.iter_participants(group.id): # iterate over group members
        if user.deleted:#  If it's a deleted account kick
            try:
                await event.client.kick_participant(group, user)
                kicked_users += 1
            except errors.ChatAdminRequiredError:
                await event.respond("ChatAdminRequiredError:  I must have the ban user permission to be able to kick deleted accounts.")
            except errors.UserAdminInvalidError:
                response = await event.respond("UserAdminInvalidError:  One of the admins has deleted their account, so I cannot kick it from the group.")
                sleep(60)
                response.delete()

    if kicked_users < 0:
        return
    await log(event, f"Kicked {kicked_users}")

    try: # Make sure the counter file doesn't already exist, otherwise create it
        with open("kick_counter.txt", "x"):
            print("Kick counter file created")
    except FileExistsError:
        pass

    with open("kick_counter.txt") as f: # Get the old value of kicked deleted accounts
        old_kicked = int(f.read())
    with open("kick_counter.txt", "w") as f: # Write new value
        f.write(str(kicked_users + old_kicked))

