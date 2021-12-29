"""Automatically kick deleted accounts

Will check active groups/channels periodically for deleted accounts, and then kick them.
"""

import time
import logging
import asyncio
import traceback
from datetime import datetime

from uniborg.util import cooldown
from telethon import events, sessions, errors, types


group_queue = asyncio.Queue()


@borg.on(borg.cmd(r"stat(s|istics)?$"))
async def stats(event):
    if not event.is_private:
        return

    await event.reply(f"I have kicked a total of `{storage.kick_counter}` deleted accounts.")


@borg.on(events.NewMessage(func=lambda e: not e.is_private))
@cooldown(60 * 60 * 24) # Only activate at minimum once a day
async def on_message(event):
    await group_queue.put(event)


async def return_deleted(group_id, deleted_admin, deleted_users=None, filter=None, total_users=0):
    if deleted_users is None:
        deleted_users = set()

    async for user in borg.iter_participants(group_id, filter=filter):
        if not user.deleted: # if it's not a deleted account; ignore
            total_users += 1
            continue
        try:
            if str(user.id) in deleted_admin[str(group_id)]: # if the account is known to be an admin; ignore
                continue
        except KeyError:
            pass

        deleted_users.add(user.id)

    return deleted_users, total_users


async def leave_chat(event, group_id):
    deleted_admin = storage.deleted_admin or dict()

    try:
        deleted_admin.pop(str(group_id))
    except KeyError:
        pass

    try:
        await borg.kick_participant(group_id, "me")
    except (errors.UserNotParticipantError, errors.ChannelPrivateError):
        pass

    storage.deleted_admin = deleted_admin


async def delete_response(event, response=list()):
    if not response:
        return

    await asyncio.sleep(60)
    try:
        for m in response:
            await m.delete()
    except errors.ChannelPrivateError:
        return


async def kick_deleted(event):
    group = event.chat_id
    deleted_group_admins = set()
    deleted_admin = storage.deleted_admin or dict()
    kicked_users = 0 # the amount of kicked users for stats
    response = list() # a list of error responses to delete later
    has_erred = False

    try:
        # iterate over users
        deleted_users, total_users = await return_deleted(group, deleted_admin)

        # iterate over banned users
        deleted_users, total_users = await return_deleted(group, deleted_admin, deleted_users,
            types.ChannelParticipantsKicked, total_users
            )
    except (AttributeError, TypeError):
        # some dumb telegram thing
        return

    except (errors.ChatAdminRequiredError, errors.ChannelPrivateError): # if bot doesn't have the right permissions; leave
        try:
            response.append(await event.respond(
                "ChatAdminRequiredError:  "
                + "I must have the ban user permission to be able to kick deleted accounts.  "
                + "Please add me back as an admin."))
        except (errors.ChatWriteForbiddenError, errors.ChatAdminRequiredError):
            pass
        logger.info(f"{event.chat_id}:  Invalid permissions, leaving chat")
        await leave_chat(event, group)

    for user in deleted_users:
        if not deleted_users:
            break
        try:
            await borg.kick_participant(group, user)
            kicked_users += 1

        except errors.UserAdminInvalidError: # if the deleted account is an admin; save the id and send error
            deleted_group_admins.add(f"{user}") # save id
            if has_erred: # don't send error if this has already happened
                continue
            has_erred = True
            try:
                response.append(await event.respond(
                    "UserAdminInvalidError:  "
                    + "An admin has deleted their account, so I cannot kick it from the group.  "
                    +  "Please remove them manually."))
            except (errors.ChatWriteForbiddenError, errors.ChatAdminRequiredError):
                pass

        except errors.ChatAdminRequiredError: # if bot doesn't have the right permissions; leave
            try:
                response.append(await event.respond(
                    "ChatAdminRequiredError:  "
                    + "I must have the ban user permission to be able to kick deleted accounts.  "
                    + "Please add me back as an admin."))
                break
            except errors.ChatAdminRequiredError:
                pass
            logger.info(f"{event.chat_id}:  Invalid permissions, leaving chat")
            await leave_chat(event, group)

        except (errors.ChannelPrivateError, errors.ChatWriteForbiddenError):
            logger.info(f"{event.chat_id}:  Invalid permissions, leaving chat")
            await leave_chat(event, group)

    loop = asyncio.get_event_loop()
    loop.create_task(delete_response(event, response=response))

    if deleted_group_admins:
        deleted_admin = storage.deleted_admin
        try:
            deleted_admin[group].update(deleted_group_admins)
        except KeyError:
            deleted_admin[group] = deleted_group_admins
        storage.deleted_admin = deleted_admin

    triggered = event.date.strftime('%y-%m-%d %H:%M:%S')
    logger.info(f"{event.chat_id}:  Kicked {kicked_users}/{total_users} {triggered}")

    kick_counter = storage.kick_counter or 0
    if kick_counter is None:
        kick_counter = 0
    kick_counter = int(kick_counter)
    storage.kick_counter = str(kick_counter + kicked_users)


async def iter_queue():
    global group_queue
    while True:
        event = await group_queue.get()
        a = time.time()
        try:
            await kick_deleted(event)
        except Exception as e:
            tb = traceback.format_exc()
            logger.warn(f"An error occured:\n {tb}")
            await borg.send_message(-1001142596298, f"```{e}\n\n{tb}```")
            continue
        b = time.time() - a
        delay = a - event.date.timestamp()
        logger.info(f"{event.chat_id}:  Took {b:.3f}s, {delay:.3f}s delay")


def unload():
    for group_loop in loops:
        group_loop.cancel()
        group_loop

loops = []
for i in range(3):
    group_loop = asyncio.ensure_future(iter_queue())
