# Copyright (c) 2020 Slavfox
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import atexit
import json
import logging
import random
import re
import shutil

import discord
from discord.ext import tasks
from emmett.commands import COMMANDS
from emmett.markov import Text, corpus_plus_sentence, make_response
from emmett.settings import (
    DISCORD_TOKEN,
    MODEL_PATH,
    REVERSE_MODEL_PATH,
)
from helpers import cycle_presence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("emmett")


class Emmett(discord.Client):
    def __init__(self):
        super().__init__()
        self.current_presence = None
        self.corpus = None
        self.reverse_corpus = None
        with MODEL_PATH.open() as f:
            self.corpus = Text.from_dict(json.load(f))
        with REVERSE_MODEL_PATH.open() as f:
            self.reverse_corpus = Text.from_dict(json.load(f))
        atexit.register(self.save_corpus)

    async def process_command(self, message: discord.Message):
        command = message.content.lower()[len("emmett: ") :]
        for regex, coro in COMMANDS.items():
            if re.match(regex, command):
                return await coro(self, message)
        raise ValueError("Not a command!")

    async def on_ready(self):
        logger.info("Successfully logged in as %s", self.user)
        self.cycle_presence.start()

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        content = message.content.lower()
        is_command = content.startswith("emmett: ")
        if is_command:
            try:
                return await self.process_command(message)
            except ValueError:
                pass
        content = self.sanitize(content)
        response = self.maybe_respond(
            content,
            author=message.author.display_name.lower(),
            forced=self.user in message.mentions,
        )
        if response:
            logger.info("Responded to '%s'", content)
            await message.channel.send(response)
        if not self.user in message.mentions:
            self.learn_from(content)

    def maybe_respond(self, prompt: str, author, forced=False):
        will_respond = forced
        if (not will_respond) and "emmett" in prompt:
            will_respond = random.random() < 0.15
        will_respond = will_respond or (random.random() < 0.025)
        if not will_respond:
            return None

        return make_response(self, prompt, author)

    def sanitize(self, message: str) -> str:
        return re.sub(
            f"{self.user.mention}|<@!{self.user.id}>", "", message
        ).strip()

    def learn_from(self, sentence: str):
        self.corpus = corpus_plus_sentence(sentence, self.corpus)
        self.reverse_corpus = corpus_plus_sentence(
            sentence[::-1], self.reverse_corpus
        )

    def save_corpus(self):
        logger.info("Saving corpus backup...")
        with MODEL_PATH.with_suffix(".json.backup").open("w") as f:
            f.write(self.corpus.to_json())
        shutil.copy(MODEL_PATH.with_suffix(".json.backup"), MODEL_PATH)
        with REVERSE_MODEL_PATH.with_suffix(".json.backup").open("w") as f:
            f.write(self.reverse_corpus.to_json())
        shutil.copy(
            REVERSE_MODEL_PATH.with_suffix(".json.backup"), REVERSE_MODEL_PATH
        )
        logger.info("Done!")

    cycle_presence = tasks.loop(minutes=30)(cycle_presence)


emmett = Emmett()

if __name__ == "__main__":
    emmett.run(DISCORD_TOKEN)
