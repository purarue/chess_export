# chess_export

[![PyPi version](https://img.shields.io/pypi/v/chess_export.svg)](https://pypi.python.org/pypi/chess_export) [![Python 3.7|3.8|3.9|3.10](https://img.shields.io/pypi/pyversions/chess_export.svg)](https://pypi.python.org/pypi/chess_export) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

Export your (or someone else's) chess.com/lichess.org games using their APIs

- Chess.com requires no authentication, see their [public API docs](https://www.chess.com/news/view/published-data-api)
- Lichess requires you to create a token, you can do so by going [here](https://lichess.org/account/oauth/token/create?description=lichess+export) (this requires no extra scopes)

## Installation

Requires `python3.8+`

To install with pip, run:

    pip install chess-export

## Usage

Each subcommand (`chessdotcom`/`lichess`) has an `export` and `inspect` command -- `export` prints data about your games as JSON, `inspect` reads that dumped info so you can use it in the REPL.

The `inspect` command just accepts the file as the first argument, like `chess_export lichess inspect data.json` or `chess_export chessdotcom inspect data.json`

### chessdotcom export

The only required argument is your username, the API serves public data and has no serial rate limit

```
$ chess_export chessdotcom export purarue >data.json
Requesting https://api.chess.com/pub/player/purarue/games/archives
Requesting https://api.chess.com/pub/player/purarue/games/2021/01
...
```

If you're getting 403 errors, you may have to supply a user agent with your email, see [this forum thread](https://www.chess.com/clubs/forum/view/error-403-in-member-profile)

To do that, you can pass the `--user-agent-email` flag or set the `CHESSDOTCOM_USER_AGENT_EMAIL` environment variable.

### lichess export

Requires your username and a [token](https://lichess.org/account/oauth/token/create?description=lichess+export) (this requires no extra scopes). The token can be provided with the `--token` flag or by setting the `LICHESS_TOKEN` environment variable.

```
$ chess_export lichess export purarue > data.json
Requesting https://lichess.org/api/games/user/purarue?pgnInJson=true
```

### Example

The games are described in [`PGN`](https://en.wikipedia.org/wiki/Portable_Game_Notation) (which can be parsed using the [`chess`](https://python-chess.readthedocs.io/en/latest/pgn.html) package)

```
$ chess_export chessdotcom export purarue >data.json
Requesting https://api.chess.com/pub/player/purarue/games/archives
Requesting https://api.chess.com/pub/player/purarue/games/2021/01
Requesting https://api.chess.com/pub/player/purarue/games/2021/02
$ chess_export chessdotcom inspect data.json

In [1]: import io, chess.pgn

In [2]: game = chess.pgn.read_game(io.StringIO(games[0].pgn))

In [3]: for move in game.mainline_moves():
   ...:     print(move)
   ...:
e2e4
e7e6
b1c3
d8f6
d2d3
f8c5
d3d4
c5d4
f2f3
```

The information returned by `chess.com`/`lichess` are slightly different, see the [lichess/model.py](chess_export/lichess/model.py) and [chessdotcom/model.py](chess_export/chessdotcom/model.py) files for reference

### Tests

```bash
git clone 'https://github.com/purarue/chess_export'
cd ./chess_export
pip install '.[testing]'
mypy ./chess_export
```
