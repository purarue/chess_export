import time
import json
from typing import Any, Union
from functools import partial
from pathlib import Path
from enum import Enum

import click
import requests

PathIsh = Union[str, Path]


def handle_path(path: PathIsh) -> Path:
    if isinstance(path, str):
        path = Path(path)
    return path


eprint = partial(click.echo, err=True)

Json = Any

BACKOFF_TIME = 15
SLEEP_TIME = 0.5


def safe_request(
    url: str,
    sleep_time: float | None = None,
    backoff_time: float | None = None,
    requested_count: int = 0,
    **kwargs: Any,
) -> requests.Response:
    eprint(f"Requesting {url}")
    resp: requests.Response = requests.get(url, **kwargs)
    # https://www.chess.com/clubs/forum/view/error-403-when-accessed-from-php
    # sometimes it seems this fails with a 403 when the servers are too overloaded?
    # has a title that says 'Just a moment...'
    if resp.status_code > 400 and resp.status_code != 404:
        eprint(f"Error: Received {resp.status_code} error, waiting...")
        eprint(f"Text: {resp.text}")
        eprint(f"Headers: {json.dumps(dict(resp.headers), indent=2)}")
        time.sleep(backoff_time or BACKOFF_TIME)
        if requested_count > 3:
            resp.raise_for_status()
        # recursive call
        return safe_request(
            url,
            requested_count=requested_count + 1,
            backoff_time=backoff_time,
            sleep_time=sleep_time,
            **kwargs,
        )
    else:
        if resp.status_code != 200:
            eprint(f"Warning: {url} received non 200 exit code: {resp.status_code}")
        time.sleep(sleep_time or SLEEP_TIME)
        return resp


def safe_request_json(
    url: str,
    sleep_time: float | None = None,
    backoff_time: float | None = None,
    **kwargs: Any,
) -> Json:
    req: requests.Response | None = None
    try:
        req = safe_request(url, sleep_time, backoff_time, **kwargs)
        return req.json()
    except requests.exceptions.JSONDecodeError as e:
        eprint(f"Warning: {url} received non-JSON response, retrying...")
        if req:
            eprint(req.text)
            raise e


class Result(Enum):
    WON = "won"
    LOSS = "loss"
    DRAW = "draw"
