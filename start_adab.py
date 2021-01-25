"""This is a bot for kicking deleted accounts from groups.
I will check for deleted accounts in active groups once an hour, but only if the group is active.
It requires the `ban user` permission in groups, and any permission in channels.

[Bot support](https://github.com/Qwerty-Space/AntiDeletedAccountsBot/issues)
[Announcements & Updates](https://t.me/joinchat/AAAAAFFqkyB7YPH6RtPbgw)
See /help for more info.
"""

from asyncio import sleep
from telethon import events, errors


# /start
@borg.on(borg.cmd(r"start$"))
async def on_start(event):
    if event.is_private:    # If command was sent in private
        await event.respond(__doc__, link_preview=False)


# Reply when added to group
@borg.on(events.ChatAction(func=lambda e:e.user_added and e.is_group))
async def added_to_group(event):
    me = (await event.client.get_me()).id

    response = None
    # Check which users were added to the group,
    # if the bot is amongst them, send the message
    for u in event.users:
        if me == u.id:
            response = await event.respond(__doc__, link_preview=False)

    if not response:
        return

    # Delete the message after a minute
    await sleep(60)
    try:
        await response.delete()
    except errors.ChannelPrivateError:
        return
