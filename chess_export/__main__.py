import json
from typing import Optional

import click

from .common import Json
from .chessdotcom.export import get_player_games as chessdotcom_get_games
from .chessdotcom.model import ChessDotComGame, from_export as chessdotcom_from_export

from .lichess.export import get_player_games as lichess_get_games
from .lichess.model import LichessGame, from_export as lichess_from_export


@click.group()
def main() -> None:
    """
    Export your chess (lichess/chess.com) games using their respective APIs
    """


@main.group()
def chessdotcom() -> None:
    """chess.com module"""


@chessdotcom.command(name="export")
@click.option(
    "--user-agent-email",
    help="Email to use as User-Agent header, if you're getting 403 errors",
    type=str,
    default=None,
    envvar="CHESSDOTCOM_USER_AGENT_EMAIL",
    show_envvar=True,
)
@click.argument("username", type=str)
def chessdotcom_export(username: str, user_agent_email: Optional[str]) -> None:
    """
    Export your chess.com games
    """
    games: list[Json] = list(chessdotcom_get_games(username, user_agent_email))
    click.echo(json.dumps(games, sort_keys=True))


@chessdotcom.command(name="inspect")
@click.argument(
    "FROM_FILE",
    type=click.Path(exists=True),
    required=True,
)
def chessdotcom_inspect(from_file: str) -> None:
    """
    Parse an exported chess.com JSON file and interact with it
    """
    games: list[ChessDotComGame] = list(chessdotcom_from_export(from_file))  # noqa
    click.secho("Use the 'games' variable to interact", fg="green")
    import IPython  # type: ignore[import]

    IPython.embed()  # type: ignore[no-untyped-call]


@main.group()
def lichess() -> None:
    """lichess.org module"""


@lichess.command(name="export")
@click.option(
    "--token",
    envvar="LICHESS_TOKEN",
    type=str,
    required=True,
    help="Lichess Personal API Access Token. See https://lichess.org/account/oauth/token",
)
@click.argument("username", type=str)
def lichess_export(username: str, token: str) -> None:
    """
    Export your lichess games
    """
    games: list[Json] = list(lichess_get_games(username, token=token))
    click.echo(json.dumps(games, sort_keys=True))


@lichess.command(name="inspect")
@click.argument(
    "FROM_FILE",
    type=click.Path(exists=True),
    required=True,
)
def lichess_inspect(from_file: str) -> None:
    """
    Parse an exported chess.com JSON file and interact with it
    """
    games: list[LichessGame] = list(lichess_from_export(from_file))  # noqa
    click.secho("Use the 'games' variable to interact", fg="green")
    import IPython  # type: ignore[import]

    IPython.embed()  # type: ignore[no-untyped-call]


if __name__ == "__main__":
    main(prog_name="chessdotcom_export")
