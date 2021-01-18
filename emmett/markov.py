# Copyright (c) 2020 Slavfox
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import logging
import random
from typing import List, Tuple

import emmett.settings as cfg
import markovify

logger = logging.getLogger("emmett")


class Text(markovify.Text):
    def sentence_split(self, text):
        return text.split("<ENDMSG>")

    def make_sentence(
        self, init_state=None, max_chars=64, min_chars=0, **kwargs
    ):
        """
        Tries making a sentence of no more than `max_chars` characters and optionally
        no less than `min_chars` characters, passing **kwargs to `self.make_sentence`.
        """
        tries = kwargs.get("tries", 10)

        for _ in range(tries):
            sentence = super().make_sentence(init_state, **kwargs)
            if sentence and min_chars <= len(sentence) <= max_chars:
                return sentence


def get_start_choices(message: str) -> Tuple[List[str], List[float]]:
    """Return a tuple of possible anchors for a response and their weights."""
    words = message.split()
    if len(words) <= 1:
        return [message], [1]
    start_states = []
    weights = []
    for i, word in enumerate(words[:-1], start=1):
        state = f"{word} {words[i]}".strip()
        word = word.strip()
        start_states.append(word)
        weights.append(len(word) + i)
        start_states.append(state)
        weights.append(len(state) + (2 * i) + 1)
    start_states.append(words[-1])
    weights.append(len(words[-1]) + len(words))
    return start_states, weights


def corpus_plus_sentence(sentence: str, corpus: Text) -> Text:
    try:
        return markovify.combine(
            [
                corpus,
                Text(sentence),
            ]
        )
    except KeyError:  # ignore
        return corpus


def make_response(emmett, message, author=""):
    if message.strip().startswith("vibe check "):
        message = message[len("vibe check "):].strip()
    if message.startswith("emmett"):
        message = message[len("emmett") :].strip()
    msg = None
    if random.random() < cfg.AUTHOR_RESPONSE_PROBABILITY:
        message += f" {author}"
    if random.random() < cfg.CONTEXT_RESPONSE_PROBABILITY:
        logger.debug("Trying to respond with context")
        choices, weights = get_start_choices(message)
        for i in range(10):
            start = ""
            end = ""
            word = random.choices(choices, weights)[0]
            logging.debug(f"Attempt %s: using '%s' as seed", i, word)
            if random.random() < cfg.START_RESPONSE_PROBABILITY:
                try:
                    start = emmett.reverse_corpus.make_sentence_with_start(
                        word[::-1], strict=False
                    )[::-1]
                except KeyError:
                    pass
                except (markovify.text.ParamError, ValueError) as e:
                    pass
            if random.random() < cfg.END_RESPONSE_PROBABILITY:
                try:
                    word = random.choices(choices, weights)[0]
                    end = emmett.corpus.make_sentence_with_start(
                        word, strict=False
                    )
                except KeyError:
                    pass
                except (markovify.text.ParamError, ValueError) as e:
                    pass
            if start.endswith(word) and end.startswith(word):
                end = end[len(word) :].strip()
            maybe_msg = f"{start} {end}".strip()
            if maybe_msg:
                msg = maybe_msg
                logging.info(f"Used '{word}' as anchor")
                break
    if not msg:
        logger.debug("Responding randomly")
        msg = emmett.corpus.make_sentence(tries=100)
    elif random.random() < 0.1:
        msg += " " + random.choice(cfg.EMOJI)
    if not msg:
        logging.error("Failed to respond to %s", message)
        msg = random.choice(cfg.EMOJI)
    logger.info(f"Response: %s", msg)
    return msg.replace("@", "\\@")
