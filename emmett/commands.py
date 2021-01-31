# Copyright (c) 2020 Slavfox
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import logging
import os
import random
import socket
import subprocess
import sys
from textwrap import dedent
from time import perf_counter

import emmett.settings as cfg
import psutil
from discord import File
from helpers import choose, cycle_presence, system_temp, vibe

COMMANDS = {}
logger = logging.getLogger("emmett")


def command(regex):
    def decorator(f):
        COMMANDS[regex] = f
        return f

    return decorator


def owner_only(command):
    async def decorated(bot, message):
        if message.author.id != cfg.OWNER_ID:
            return await message.channel.send(
                f"Sorry, only fox is authorized to do this "
                f"{random.choice(cfg.EMOJI)}"
            )
        return await command(bot, message)

    return decorated


@command("^choose")
async def choose_command(bot, message):
    try:
        return await message.channel.send(
            choose(message.content[len("emmett: choose") :])
        )
    except ValueError:
        return await message.channel.send("What am I supposed to choose from?")


@command("^change status$")
@owner_only
async def change_status(bot, message):
    activity_name = await cycle_presence(bot)
    return await message.channel.send(
        f"Status is now: {activity_name} {vibe()}"
    )


@command("^current vibe$")
async def current_vibe(bot, message):
    return await message.channel.send(f"Current vibe: {vibe()}")


@command("^back up your model")
@owner_only
async def backup(bot, message):
    start = perf_counter()
    await message.channel.send("Backing up model... :floppy_disk:")
    bot.save_corpus()
    return await message.channel.send(
        f"Model backed up in {perf_counter()-start:2f} seconds "
        f":white_check_mark:"
    )


@command("^image")
async def image(bot, message):
    img = None
    parts = message.content.split()
    if len(parts) > 1:
        filename = message.content.split()[-1].replace("..", "")
        if filename.startswith("/"):
            filename = filename[1:]
        path = cfg.DATA_DIR / "reactions" / filename
        logger.info("trying to send %s", repr(path.resolve()))
        if path.is_file():
            img = path
    if not img:
        img = random.choice(list(cfg.DATA_DIR.glob(cfg.REACTION_GLOB)))
    with img.open("rb") as f:
        return await message.channel.send(
            file=File(f, filename=f"pensive{img.suffix}")
        )


@command("^reboot$")
@owner_only
async def reboot(bot, message):
    await message.channel.send("Shutdown in progress...")
    bot.save_corpus()
    await message.channel.send("Corpus backed up :white_check_mark:")
    subprocess.run(["git", "pull"], cwd=cfg.REPO_ROOT.resolve())
    await message.channel.send("Code updated :white_check_mark:")
    await message.channel.send("Rebooting!")
    os.execl(sys.executable, sys.executable, *sys.argv)


@command("(run a level \d+ )?diagnostic$")
async def diagnostic(bot, message):
    start = perf_counter()
    uptime = subprocess.run(
        ["uptime", "-p"], stdout=subprocess.PIPE
    ).stdout.decode("utf-8")
    virtual_memory = psutil.virtual_memory()
    used_memory = (virtual_memory.total - virtual_memory.available) / 1_048_576
    model_size = os.path.getsize(cfg.MODEL_PATH) + os.path.getsize(
        cfg.REVERSE_MODEL_PATH
    )
    return await message.channel.send(
        dedent(
            f"""\
        `emmett@{socket.gethostname()}`
        {uptime}
        Running on: 
        ```
        {{}}
        ```
        CPU usage: `{psutil.cpu_percent():n}%`
        Memory usage: `{virtual_memory.percent}% ({used_memory:n} MiB)`
        System temperature: `{system_temp()}°C`
        
        Latency: `{bot.latency*1000:n} ms`
        Model size: `{model_size/1_048_576:.3f} MiB`
        Current vibe: {vibe()}
        
        **Weights:**
        base: {cfg.UNPROMPTED_RESPONSE_PROBABILITY}
        name: {cfg.EMMETT_RESPONSE_PROBABILITY}
        context: {cfg.CONTEXT_RESPONSE_PROBABILITY}
        author name: {cfg.AUTHOR_RESPONSE_PROBABILITY}
        start: {cfg.START_RESPONSE_PROBABILITY}
        end: {cfg.END_RESPONSE_PROBABILITY}
        emoji: {cfg.EMOJI_PROBABILITY}
        steam status: {cfg.STEAM_STATUS_PROBABILITY}
        image: {cfg.IMAGE_RESPONSE_PROBABILITY}
        mixed: {cfg.IMAGE_TEXT_RESPONSE_PROBABILITY}
        
        Diagnostic took: `{(perf_counter() - start)*1000:n} ms`
        """
        ).format(sys.version)
    )
