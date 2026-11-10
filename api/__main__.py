"""Entry point: `python -m api [load|serve]`.

No argument loads missing data and serves the API (api/route.py).
"""
from __future__ import annotations

import argparse
import logging

from api.load import ensure_data_loaded


def serve(host: str, port: int) -> None:
    """Start the API with uvicorn."""
    import uvicorn

    uvicorn.run("api.route:app", host=host, port=port)


def main(argv: list[str] | None = None) -> None:
    """Run the command named on the command line."""
    from api.route import DEFAULT_PORT

    parser = argparse.ArgumentParser(prog="python -m api")
    parser.add_argument("command", nargs="?", choices=["load", "serve"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)

    if args.command in (None, "load"):
        ensure_data_loaded()
    if args.command in (None, "serve"):
        serve(args.host, args.port)


if __name__ == "__main__":
    main()
