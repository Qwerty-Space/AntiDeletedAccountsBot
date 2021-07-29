"""This is a bot for kicking deleted accounts from groups.
I will check for deleted accounts in __active__ groups once every 6 hours.
I require the `ban user` permission in groups, and any permission in channels.

I might take a few minutes to work the first time you add me to a group, so please be patient.

[Bot support](https://github.com/Qwerty-Space/AntiDeletedAccountsBot/discussions)
[Bug reporting](https://github.com/Qwerty-Space/AntiDeletedAccountsBot/issues)
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
            try:
                response = await event.respond(__doc__, link_preview=False)
                break
            except errors.ChatWriteForbiddenError:
                break

    if not response:
        return

    # Delete the message after a minute
    await sleep(60)
    try:
        await response.delete()
    except errors.ChannelPrivateError:
        return
