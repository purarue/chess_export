"""
Request/Export your games from chess.com
"""

import os
from typing import Iterator, List, Optional, Dict

from ..common import Json, safe_request_json

BASE_URL = "https://api.chess.com/pub/"


def _user_agent(user_agent_email: Optional[str] = None) -> Dict[str, str]:
    if user_agent_email is None and "CHESSDOTCOM_USER_AGENT_EMAIL" in os.environ:
        user_agent_email = os.environ["CHESSDOTCOM_USER_AGENT_EMAIL"]
    if user_agent_email:
        return {
            "User-Agent": f"https://github.com/purarue/chess_export {user_agent_email}"
        }
    return {}


def get_player_game_archives(
    username: str, user_agent_email: Optional[str] = None
) -> List[str]:
    """Returns a list of monthly archive URLs for the user"""
    url = BASE_URL + "/".join(("player", username, "games", "archives"))
    mresp = safe_request_json(url, headers=_user_agent(user_agent_email))
    if "archives" not in mresp:
        raise RuntimeError(f"Unexpected response from {url}: {mresp}")
    return list(mresp["archives"])


def get_player_games(
    username: str, user_agent_email: Optional[str] = None
) -> Iterator[Json]:
    """Returns all accessible games, using the monthly archive as the source"""
    for archive_url in get_player_game_archives(username, user_agent_email):
        month_games = safe_request_json(
            archive_url, headers=_user_agent(user_agent_email)
        )
        if "games" in month_games:
            yield from month_games["games"]
        else:
            raise RuntimeError(f"Unexpected response from {archive_url}: {month_games}")
