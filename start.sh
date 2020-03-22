#!/bin/bash
# Start AntiDeletedAccountsBot

tmux new -s AntiDeletedAccountsBot "python3 bot.py 2>&1 | tee log.txt"
