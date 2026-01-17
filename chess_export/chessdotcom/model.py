"""
Parse the Game response JSON object from chess.com
"""

import json

from datetime import datetime, timezone
from typing import NamedTuple
from collections.abc import Iterator

from ..common import Json, Result, PathIsh, handle_path


class ChessDotComUserRating(NamedTuple):
    rating: int
    result: str
    id_: str
    username: str

    @classmethod
    def from_api_response(cls, api_resp: Json) -> "ChessDotComUserRating":
        return cls(
            rating=api_resp["rating"],
            result=api_resp["result"],
            id_=api_resp["@id"],
            username=api_resp["username"],
        )


class ChessDotComGame(NamedTuple):
    url: str
    pgn: str | None
    fen: str
    time_control: str
    end_time: datetime
    rated: bool
    time_class: str
    rules: str
    white: ChessDotComUserRating
    black: ChessDotComUserRating

    def result(self, username: str) -> Result | None:
        """
        Return the result of the game for the given username
        """
        result: ChessDotComUserRating
        if self.white.username == username:
            result = self.white
        elif self.black.username == username:
            result = self.black
        else:
            # username not in game
            return None
        if result.result == "win":
            return Result.WON
        elif result.result in {"resigned", "timeout", "abandoned", "checkmated"}:
            return Result.LOSS
        elif result.result in {
            "agreed",
            "stalemate",
            "repetition",
            "insufficient",
            "timevsinsufficient",
            "50move",
        }:
            return Result.DRAW
        else:
            return None

    @classmethod
    def from_api_response(cls, api_resp: Json) -> "ChessDotComGame":
        # the pgn typically exists, but may not for some older games?, unsure why
        return cls(
            url=api_resp["url"],
            pgn=api_resp.get("pgn"),
            fen=api_resp["fen"],
            time_control=api_resp["time_control"],
            end_time=datetime.fromtimestamp(api_resp["end_time"], tz=timezone.utc),
            rated=api_resp["rated"],
            time_class=api_resp["time_class"],
            rules=api_resp["rules"],
            white=ChessDotComUserRating.from_api_response(api_resp["white"]),
            black=ChessDotComUserRating.from_api_response(api_resp["black"]),
        )


def from_export(filepath: PathIsh) -> Iterator[ChessDotComGame]:
    """
    Parse a chess.com exported file
    """
    with handle_path(filepath).open() as f:
        for gobj in json.load(f):
            yield ChessDotComGame.from_api_response(gobj)
