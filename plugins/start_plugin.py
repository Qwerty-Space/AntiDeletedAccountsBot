"""Start message

pattern: `/start$`
"""

from asyncio import sleep
from .global_functions import log
from telethon import client, events, errors


# /start
@events.register(events.NewMessage(pattern=r"/start$"))
async def on_start(event):
    if event.is_private:    # If command was sent in private
        await log(event)    # Logs the event
        await event.respond(
            "This is a bot for kicking deleted accounts from groups.  "
            + "It requires the `ban user` permission in groups, and any permission in channels.\n\n"
            + "See /help for more info."
)


# Reply when added to group
@events.register(events.ChatAction(func=lambda e:e.user_added and e.is_group))
async def added_to_group(event):
    group = await event.get_chat() # Get group object
    me = (await event.client.get_me()).id

    response = None
    for u in event.users:
        if me == u.id:
            response = await event.respond(
                "I will check for deleted accounts in active groups once an hour.\n"
                + "[Bot support](https://github.com/Qwerty-Space/AntiDeletedAccountsBot/issues)\n"
                + "This message will self destruct",
                link_preview=False)

    if not response:
        return

    await sleep(60)
    try:
        await response.delete()
    except errors.ChannelPrivateError:
        return
