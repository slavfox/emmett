# Copyright (c) 2020 Slavfox
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import json
import random
import re
import subprocess
from time import time
from urllib.error import URLError
from urllib.request import urlopen

import discord
import emmett.settings as cfg


def vibe():
    return cfg.EMOJI[hash(str(int(time() / 100))) % len(cfg.EMOJI)]


def system_temp():
    try:
        temps = json.loads(
            subprocess.run(["sensors", "-j"], stdout=subprocess.PIPE).stdout
        )
    except json.decoder.JSONDecodeError:
        return 40.0
    try:
        return temps["coretemp-isa-0000"]["Package id 0"]["temp1_input"]
    except KeyError:
        return 40.0


def get_random_top100_steam_game():
    games = json.load(
        urlopen("https://steamspy.com/api.php?request=top100in2weeks")
    )
    game = random.choice(list(games.keys()))
    return games[game]["name"]


def choose(msg: discord.Message):
    if msg.startswith(":"):
        msg = msg[1:]
    msg = msg.strip()
    options = [
        choice.strip()
        for choice in re.split(",|;| or ", msg)
        if choice.strip()
    ]
    if not options:
        raise ValueError("No options provided!")
    choice_msg = random.choice(cfg.CHOICE_MSGS)
    return choice_msg.format(random.choice(options))


async def cycle_presence(bot):
    activity = None
    if random.random() < cfg.STEAM_STATUS_PROBABILITY:
        try:
            activity = discord.Game(get_random_top100_steam_game())
        except (URLError, ValueError):
            pass
    if not activity:
        activity = random.choice(cfg.PRESENCES)
    await bot.change_presence(activity=activity)
    return activity.name
