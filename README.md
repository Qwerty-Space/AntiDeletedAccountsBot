# AntiDeletedAccountsBot (ADAB)
Automatically kick deleted accounts

Based on [uniborg](Qwerty-Space/uniborg), a pluggable 
[``asyncio``](https://docs.python.org/3/library/asyncio.html) 
[Telegram](https://telegram.org) userbot based on
[Telethon](LonamiWebs/Telethon).


## Installation
1.  Clone the AntiDeletedAccounts Bot branch of Uniborg

```sh
git clone --single-branch --branch antideletedaccounts https://github.com/Qwerty-Space/uniborg.git AntiDeletedAccountsBot
```

2.  Add your config into config.py, following the instructions in config.example.py

```python
id = 12345  # Your API ID
hash = "11223344556677889900AABBCCDDEEFF"  # API Hash
admins = 12346789  # Any "admins" for the bot that will be able to reload the plugins
```

5.  Run `python stdbot.py`


## FAQ
1.  A user deleted their account, why hasn't the bot kicked them yet?

*  ADAB only checks for deleted accounts ONCE every 6 hours at most.  And it will only check for deleted accounts if a message was sent to the group.  This behaviour will keep the bot from slowing down too much by filtering out inactive groups.

2.  Does ADAB kick or ban deleted accounts?

*  ADAB kicks deleted accounts (ban + unban).

3.  Does ADAB work in channels?

*  Yes.  It doesn't matter what permission you give it in broadcast channels, all channel admins have the permission to kick/ban.

4.  How do I run it persistently, or in the background?

*  Use something like tmux: `tmux new -ds AntiDeletedAccountsBot "python3 stdbot.py"`

See running example on Telegram [@AntiDeletedAccounts_Bot](https://t.me/AntiDeletedAccounts_Bot)
