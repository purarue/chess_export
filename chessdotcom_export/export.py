"""
Request/Export your games from chess.com
"""

import time
from typing import Iterator, Dict, List
from functools import partial

import requests
import click

from .common import Json
from .model import Game

eprint = partial(click.echo, err=True)

CHESSDOTCOM_BASE_URL = "https://api.chess.com/pub/"

# serial access limit unlimited, but may run into 429s if something goes wrong
def chessdotcom_request(url: str) -> Json:
    """
    Error handling/parsing for chess.com requests
    """
    eprint(f"Requesting {url}")
    resp: requests.Response = requests.get(url)
    if resp.status_code == 429:
        eprint("Error: Recieved 429 error, waiting...")
        time.sleep(4)
        # recursive call
        return chessdotcom_request(url)
    else:
        if resp.status_code != 200:
            eprint(f"Warning: {url} recieved non 200 exit code: {resp.status_code}")
        return resp.json()


def _key_or_error(resp: Json, key: str) -> Json:
    """Get value from dictionary with the key. Throw a RuntimeError if its not present on the object"""
    if key in resp:
        return resp[key]
    else:
        raise KeyError(
            "Error: expected key {}, couldn't find on object: {}".format(key, resp)
        )


def get_player_game_archives(username: str) -> List[str]:
    """Returns a list of monthly archive URLs for the user"""
    url = CHESSDOTCOM_BASE_URL + "/".join(("player", username, "games", "archives"))
    mresp = chessdotcom_request(url)
    return list(mresp["archives"])


def get_player_games(username: str) -> Iterator[Game]:
    """Returns all accessible games, using the monthly archive as the source"""
    for archive_url in get_player_game_archives(username):
        gresp = chessdotcom_request(archive_url)
        for game in gresp["games"]:
            yield Game.from_api_response(game)