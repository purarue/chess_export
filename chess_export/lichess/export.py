"""
Request/Export your games from lichess.org
"""

import json

from typing import Any, Optional
from collections.abc import Iterator
from urllib.parse import urlencode

from ..common import Json, safe_request

BASE_URL = "https://lichess.org/api"

DEFAULTS_OPTS = {"pgnInJson": "true"}


def get_player_games(
    username: str,
    *,
    token: str,
    additional_params: dict[str, Any] | None = None,
) -> Iterator[Json]:
    """Returns all accessible games, requires a personal API token"""
    if additional_params is None:
        additional_params = {}
    for k, v in DEFAULTS_OPTS.items():
        if k not in additional_params:
            additional_params[k] = v
    resp = safe_request(
        f"{BASE_URL}/games/user/{username}?{urlencode(additional_params)}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/x-ndjson"},
    )
    # one JSON object per line
    for line in resp.text.splitlines():
        if line.strip():
            yield json.loads(line)
