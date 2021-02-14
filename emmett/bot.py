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
from importlib import reload

import discord
import emmett.settings as cfg
from discord.ext import tasks
from emmett.commands import COMMANDS
from emmett.markov import Text, corpus_plus_sentence, make_response
from helpers import cycle_presence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("emmett")


class Emmett(discord.Client):
    def __init__(self):
        super().__init__()
        self.current_presence = None
        self.corpus = None
        self.reverse_corpus = None
        with cfg.MODEL_PATH.open() as f:
            self.corpus = Text.from_dict(json.load(f))
        with cfg.REVERSE_MODEL_PATH.open() as f:
            self.reverse_corpus = Text.from_dict(json.load(f))
        atexit.register(self.save_corpus)

    async def on_ready(self):
        logger.info("Successfully logged in as %s", self.user)
        self.cycle_presence.start()

    async def on_message(self, message: discord.Message):
        if message.author == self.user or message.content.startswith('.'):
            return
        reload(cfg)
        content = message.content.lower()
        if any([word in content for word in cfg.BLOCKLIST]):
            return await message.add_reaction(cfg.BLOCKLIST_TRIGGER_REACTION)
        is_command = content.startswith("emmett: ")
        if is_command:
            try:
                return await self.process_command(message)
            except ValueError:
                pass
        elif content == "oof":
            return await self.oof(message)
        elif content == "what":
            return await self.wtf(message)
        content = self.sanitize(content)
        await self.maybe_respond(
            message,
            content,
        )
        if not self.user in message.mentions:
            self.learn_from(content)

    async def process_command(self, message: discord.Message):
        command = message.content.lower()[len("emmett: ") :]
        for regex, coro in COMMANDS.items():
            if re.match(regex, command):
                return await coro(self, message)
        raise ValueError("Not a command!")

    @staticmethod
    async def oof(message: discord.Message):
        oof_img = random.choice(list(cfg.DATA_DIR.glob(cfg.OOF_GLOB)))
        with oof_img.open("rb") as f:
            await message.channel.send(
                "oof!", file=discord.File(f, filename=f"oof{oof_img.suffix}")
            )

    @staticmethod
    async def wtf(message: discord.Message):
        wtf_img = random.choice(list(cfg.DATA_DIR.glob(cfg.WHAT_GLOB)))
        with wtf_img.open("rb") as f:
            await message.channel.send(
                "what", file=discord.File(f, filename=f"what{wtf_img.suffix}")
            )

    async def maybe_respond(self, message, prompt: str):
        will_respond = self.user in message.mentions
        reply = will_respond
        if (not will_respond) and "emmett" in prompt:
            will_respond = random.random() < cfg.EMMETT_RESPONSE_PROBABILITY
        will_respond = will_respond or (
            random.random() <= cfg.UNPROMPTED_RESPONSE_PROBABILITY
        )
        if not will_respond:
            return None
        if random.random() <= cfg.IMAGE_RESPONSE_PROBABILITY:
            img = random.choice(list(cfg.DATA_DIR.glob(cfg.REACTION_GLOB)))
            logger.info("Responding with image %s", img)
            msg = None
            if random.random() <= cfg.IMAGE_TEXT_RESPONSE_PROBABILITY:
                msg = make_response(
                    self, prompt, message.author.display_name.lower()
                )
            with img.open("rb") as f:
                return await message.channel.send(
                    msg, file=discord.File(f, filename=f"pensive{img.suffix}")
                )
        response = make_response(self, prompt, message.author.display_name.lower())
        if reply:
            return await message.reply(response)
        return await message.channel.send(response)

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
        with cfg.MODEL_PATH.with_suffix(".json.backup").open("w") as f:
            f.write(self.corpus.to_json())
        shutil.copy(cfg.MODEL_PATH.with_suffix(".json.backup"), cfg.MODEL_PATH)
        with cfg.REVERSE_MODEL_PATH.with_suffix(".json.backup").open("w") as f:
            f.write(self.reverse_corpus.to_json())
        shutil.copy(
            cfg.REVERSE_MODEL_PATH.with_suffix(".json.backup"),
            cfg.REVERSE_MODEL_PATH,
        )
        logger.info("Done!")

    cycle_presence = tasks.loop(minutes=30)(cycle_presence)


emmett = Emmett()

if __name__ == "__main__":
    emmett.run(cfg.DISCORD_TOKEN)
