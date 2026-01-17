"""
Parse the Game response JSON object from lichess.org
"""

import json

from datetime import datetime, timezone
from typing import NamedTuple
from collections.abc import Iterator

from ..common import Json, Result, PathIsh, handle_path


class UserRating(NamedTuple):
    rating: int
    ratingDiff: int
    id_: str
    username: str

    @classmethod
    def from_api_response(cls, api_resp: Json) -> "UserRating":
        return cls(
            rating=api_resp["rating"],
            ratingDiff=api_resp["ratingDiff"],
            id_=api_resp["user"]["id"],
            username=api_resp["user"]["name"],
        )


def _parse_datetime_ms(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1_000, tz=timezone.utc)


class LichessGame(NamedTuple):
    game_id: str
    pgn: str | None
    moves: str
    start_time: datetime
    end_time: datetime
    rated: bool
    speed: str
    status: str
    variant: str
    perf: str
    winner: str | None
    white: UserRating
    black: UserRating

    def result(self, username: str) -> Result | None:
        winner = self.winner
        if winner is None:
            return None
        elif winner == "white" and self.white.username == username:
            return Result.WON
        elif winner == "black" and self.black.username == username:
            return Result.WON
        else:
            return Result.LOSS
        # TODO: not sure how this represents a draw?

    @classmethod
    def from_api_response(cls, api_resp: Json) -> "LichessGame":
        # the pgn typically exists, but may not for some older games?, unsure why
        return cls(
            game_id=api_resp["id"],
            start_time=_parse_datetime_ms(api_resp["createdAt"]),
            end_time=_parse_datetime_ms(api_resp["lastMoveAt"]),
            moves=api_resp["moves"],
            pgn=api_resp.get("pgn"),
            perf=api_resp["perf"],
            rated=api_resp["rated"],
            speed=api_resp["speed"],
            status=api_resp["status"],
            variant=api_resp["variant"],
            winner=api_resp.get("winner"),
            white=UserRating.from_api_response(api_resp["players"]["white"]),
            black=UserRating.from_api_response(api_resp["players"]["black"]),
        )


def from_export(filepath: PathIsh) -> Iterator[LichessGame]:
    """
    Parse a lichess.com game file
    """
    with handle_path(filepath).open() as f:
        for gobj in json.load(f):
            yield LichessGame.from_api_response(gobj)
