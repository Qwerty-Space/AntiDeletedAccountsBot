#!/bin/bash
# Start AntiDeletedAccountsBot

tmux new -ds AntiDeletedAccountsBot "python3 stdbot.py ADAB 2>&1 | tee log.txt"
