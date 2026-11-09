"""Entry point: `python -m uncf [load|serve|precompute]`.

No argument loads the data if it's missing, then serves the Results API. `precompute` still saves results
the old way (#4); the API no longer needs it.
"""
from __future__ import annotations

import argparse
import logging

from uncf import precompute


def serve(host: str, port: int) -> None:
    """Start the Results API with uvicorn."""
    import uvicorn

    uvicorn.run("uncf.api:app", host=host, port=port)


def main(argv: list[str] | None = None) -> None:
    """Run the command named on the command line."""
    from uncf.api import DEFAULT_PORT

    parser = argparse.ArgumentParser(prog="python -m uncf")
    parser.add_argument("command", nargs="?", choices=["load", "serve", "precompute"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)

    if args.command == "precompute":
        precompute.main()
        return
    if args.command in (None, "load"):
        precompute.ensure_data_loaded()
    if args.command in (None, "serve"):
        serve(args.host, args.port)


if __name__ == "__main__":
    main()
