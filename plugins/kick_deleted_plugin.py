"""Automatically kick deleted accounts

Will check active groups/channels periodically for deleted accounts, and then kick them.
"""

from telethon import client, events, sessions, errors, types
from .global_functions import log, cooldown
from asyncio import sleep


kick_counter = "kick_counter.txt"
deleted_admin = set()


async def return_deleted(client, group_id, deleted_users=set(), filter=None):
    async for user in client.iter_participants(group_id, filter=filter):
        if not user.deleted: # if it's not a deleted account; ignore
            continue
        if user.id in deleted_admin: # if the account is known to be an admin; ignore
            continue

        deleted_users.add(user)
        return deleted_users


@events.register(events.NewMessage(func=lambda e: not e.is_private))
@cooldown(60 * 60, False) # Only activate at minimum once an hour
async def kick_deleted(event):
    group = await event.get_chat() # get group object
    client = event.client # DRY

    kicked_users = 0 # the amount of kicked users for stats
    response = list() # a list of error responses to delete later
    has_erred = False

    deleted_users = await return_deleted(client, group.id) # iterate over group members
    deleted_users.update(await return_deleted(client, group.id,
                        deleted_users, types.ChannelParticipantsBanned)) # iterate over restricted users
    deleted_users.update(await return_deleted(client, group.id,
                        deleted_users, types.ChannelParticipantsKicked)) # iterate over banned users

    async for user in deleted_users:
        try:
            await client.kick_participant(group, user)
            kicked_users += 1
        except errors.ChatAdminRequiredError: # if bot doesn't have the right permissions to kick accounts; leave
            response.append(await event.respond(
                                "ChatAdminRequiredError:  "
                                + "I must have the ban user permission to be able to kick deleted accounts."
                                + "Please add me back as an admin."))
            await log(event, "Invalid permissions")
            await client.kick_participant(group, "me")
            break
        except errors.UserAdminInvalidError: # if the deleted account is an admin; save the id and send error
            deleted_admin.add(user.id) # save id
            if has_erred: # don't send error if this has already happened
                continue
            has_erred = True
            response.append(await event.respond(
                                "UserAdminInvalidError:  "
                                + "An admin has deleted their account, so I cannot kick it from the group."))

    if kicked_users >= 0:
        await log(event, f"Kicked {kicked_users}")

    with open(kick_counter) as f: # get the old value of kicked deleted accounts
        old_kicked = f.read()
        if not old_kicked:
            old_kicked = 0
    with open(kick_counter, "w") as f: # write new value
        new_val = kicked_users + int(old_kicked)
        f.write(str(new_val))

    if not response:
        return

    await sleep(60)
    try:
        for m in response:
            await m.delete()
    except errors.ChannelPrivateError:
        return
