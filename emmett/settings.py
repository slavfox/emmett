# Copyright (c) 2020 Slavfox
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import logging
import os
from pathlib import Path

from discord import Activity, ActivityType, Game

EMMETT_DIR = Path(__file__).parent
REPO_ROOT = EMMETT_DIR.parent
DATA_DIR = Path(EMMETT_DIR / "data")
MODEL_PATH = Path(DATA_DIR / "model.json")
REVERSE_MODEL_PATH = Path(DATA_DIR / "reverse_model.json")
OWNER_ID = 669078523226488833

# Chance to respond to a message without being prompted
UNPROMPTED_RESPONSE_PROBABILITY = 0.025
# Chance to respond to a message when mentioned by name
EMMETT_RESPONSE_PROBABILITY = 0.15
# Chance to use a random word from the message as context
CONTEXT_RESPONSE_PROBABILITY = 0.8
# Chance to include the author's nickname in the context
AUTHOR_RESPONSE_PROBABILITY = 0.4
# Chance to generate a prefix for the context
START_RESPONSE_PROBABILITY = 0.8
# Chance to generate a suffix for the context
END_RESPONSE_PROBABILITY = 0.8
# Chance to append an emoji
EMOJI_PROBABILITY = 0.1
# Chance to use a random top 100 Steam game as the status
STEAM_STATUS_PROBABILITY = 0.4

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
LOGGING_LEVEL = logging.INFO

EMOJI = [
    ":pensive:",
    ":confused:",
    ":cowboy:",
    ":sun_with_face:",
    ":thinking:",
    ":face_with_raised_eyebrow:",
    ":weary:",
    ":pleading_face:",
    ":rolling_eyes:",
    ":yawning_face:",
    ":face_with_hand_over_mouth:",
    ":sunglasses:",
    ":upside_down:",
    ":slight_smile:",
    ":face_with_monocle:",
    ":eggplant:",
    ":flushed:",
    ":grimacing:",
    ":frowning:",
    ":bone:",
    ":nose::astronaut:",
    ":hot_face:",
    ":eye:",
    ":eyes:",
]

PRESENCES = [
    Game("Opening up the pit"),
    Game("Drinking heavy foam coffee"),
    Game("being incinerated"),
    Game("doing captain things"),
    Game("applying to be a keeper"),
    Game("cleaning my little fangs"),
    Game("switching from femme to masc or THE FORBIDDEN ONE"),
    Game("opting in and out of context"),
    Game("🌌👃🧑‍🚀 exploring space"),
    Activity(name="vtubers", type=ActivityType.watching.value),
    Activity(name="Star Trek", type=ActivityType.watching.value),
    Activity(name="Star Trek: Voyager", type=ActivityType.watching.value),
    Activity(
        name="Star Trek: The Next Generation", type=ActivityType.watching.value
    ),
    Activity(name="Star Trek: Deep Space 9", type=ActivityType.watching.value),
    Activity(name="soul songs", type=ActivityType.listening.value),
    Activity(name="AWAY GAMES", type=ActivityType.listening.value),
    Activity(name="BLATTLE OF THE BLANDS", type=ActivityType.listening.value),
    Game("😔"),
    Game("Hades"),
    Game("Blood Bowl 2"),
    Game("Blaseball"),
    Game("BlaseBowl"),
    Game("AI Dungeon"),
    Game("Story of Seasons: Friends of Mineral Town"),
    Game("SCP - Containment Breach"),
    Game("Goat Simulator"),
    Game("Star Trek Online"),
    Game("Digits & Data 5th edition"),
    Game("Warhammer Fantasy Battles"),
    Game("Warhammer 40,000"),
    Game("Stardew Valley"),
    Game("Minecraft"),
    Game("with Carl"),
]

CHOICE_MSGS = [
    "i choose {}!",
    "{} sounds good.",
    "i'm leaning towards {}",
    "Definitely {}!",
    "{}!",
    "i think {} would be neat.",
    ":persevere: :raised_hand: anything else\n\n:smile: :point_right: {}",
    "{} :weary:",
    "{} :pleading_face:",
    "yeah, let's go with {}",
]
