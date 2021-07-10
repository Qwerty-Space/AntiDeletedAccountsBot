"""Automatically kick deleted accounts

Will check active groups/channels periodically for deleted accounts, and then kick them.
"""

import logging
import asyncio
from datetime import datetime

from uniborg.util import cooldown
from telethon import events, sessions, errors, types


group_queue = asyncio.Queue()


async def return_deleted(group_id, deleted_admin, deleted_users=None, filter=None, total_users=0):
    if deleted_users is None:
        deleted_users = set()
    async for user in borg.iter_participants(group_id, filter=filter):
        if not user.deleted: # if it's not a deleted account; ignore
            total_users += 1
            continue
        try:
            if user.id in deleted_admin[group_id]: # if the account is known to be an admin; ignore
                continue
        except KeyError:
            pass

        deleted_users.add(user.id)
    return deleted_users, total_users


@borg.on(events.NewMessage(func=lambda e: not e.is_private))
@cooldown(60 * 60 * 6) # Only activate at minimum once every 6 hours
async def on_message(event):
    await group_queue.put(event)
    logger.info(f"{event.chat_id}:  Queued")


@borg.on(borg.cmd(r"stat(s|istics)?$"))
async def stats(event):
    if not event.is_private:
        return

    await event.reply(f"I have kicked a total of `{storage.kick_counter}` deleted accounts.")


async def kick_deleted(event):
    group = event.chat_id
    deleted_group_admins = set()
    deleted_admin = storage.deleted_admin or dict()
    kicked_users = 0 # the amount of kicked users for stats
    response = list() # a list of error responses to delete later
    has_erred = False

    # iterate over users
    deleted_users, total_users = await return_deleted(group, deleted_admin=deleted_admin)
    try:
        # iterate over banned users
        new_deleted, new_total = await return_deleted(group, deleted_admin, deleted_users,
            types.ChannelParticipantsKicked, total_users
            )
        deleted_users.update(new_deleted)
        total_users += total_users
    except (AttributeError, TypeError):
        pass


    if not deleted_users:
        return


    for user in deleted_users:
        try:
            await borg.kick_participant(group, user)
            kicked_users += 1

        except errors.ChatAdminRequiredError: # if bot doesn't have the right permissions to kick accounts; leave
            try:
                response.append(await event.respond(
                    "ChatAdminRequiredError:  "
                    + "I must have the ban user permission to be able to kick deleted accounts."
                    + "Please add me back as an admin."))
            except errors.ChatWriteForbiddenError:
                pass
            logger.info(f"{event.chat_id}:  Invalid permissions, leaving chat")
            await borg.kick_participant(group, "me")
            break

        except errors.UserAdminInvalidError: # if the deleted account is an admin; save the id and send error
            deleted_group_admins.add(f"{user}") # save id
            if has_erred: # don't send error if this has already happened
                continue
            has_erred = True
            try:
                response.append(await event.respond(
                    "UserAdminInvalidError:  "
                    + "An admin has deleted their account, so I cannot kick it from the group."
                    +  "Please remove them manually."))
            except errors.ChatWriteForbiddenError:
                pass

    if deleted_group_admins:
        deleted_admin = storage.deleted_admin
        try:
            deleted_admin[group].update(deleted_group_admins)
        except KeyError:
            deleted_admin[group] = deleted_group_admins
        storage.deleted_admin = deleted_admin

    logger.info(f"{event.chat_id}:  Kicked {kicked_users} / {total_users}")

    kick_counter = int(storage.kick_counter) or 0
    storage.kick_counter = str(kick_counter + kicked_users)

    if not response:
        logger.info("no response")
        return

    await asyncio.sleep(60)
    try:
        for m in response:
            await m.delete()
    except errors.ChannelPrivateError:
        logger.info("response")
        return


async def iter_queue():
    global group_queue
    while True:
        event = await group_queue.get()
        logger.info(f"{event.chat_id} event:  {event.date.strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            await kick_deleted(event)
        except Error as e:
            tb = traceback.format_exc()
            logger.warn(f"An error occured:\n {tb}")
            await event.send_message(-1001142596298, f"{e}")


def unload():
    if group_loop:
        group_loop.cancel()
        group_loop


group_loop = asyncio.ensure_future(iter_queue())
