"""Automatically kick deleted accounts

Will check periodically on new message for deleted accounts, and then kick them.
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

    group = await event.get_chat()
    kicked_users = 0

    async for user in event.client.iter_participants(group.id):
        if user.deleted:
            await event.client.kick_participant(group, user)
            kicked_users += 1

    if kicked_users > 0:
        await log(event, f"Kicked {kicked_users}")
