from collections import defaultdict
from random import random
import inspect
import logging
import asyncio
import time


# Probability
def probability(percent):
    outcome = random() < percent
    return outcome

# Logging
async def log(event, info=""):
    sender = await event.get_sender()
    # Get the name of the command sent to the bot:
    command = inspect.currentframe().f_back.f_code.co_name
    logging.info(
        f"""[{event.date.strftime('%c')}]:
    [{sender.id}]@[{event.chat_id}] {sender.first_name}@{sender.username}: {command}
    {info}""".rstrip())

# Cooldown
def cooldown(timeout, log=True):
    def wrapper(function):
        last_called = defaultdict(int)

        async def wrapped(event, *args, **kwargs):
            current_time = time.time()
            if current_time - last_called[event.chat_id] < timeout:
                time_left = round(timeout - (current_time - last_called[event.chat_id]), 1)
                if log:
                    await log(event, f"Cooldown: {time_left}s")
                return
            last_called[event.chat_id] = current_time
            return await function(event, *args, **kwargs)
        return wrapped
    return wrapper
