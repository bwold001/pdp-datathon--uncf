"""Entry point: `python -m api [load|serve]`.

No argument loads missing data and serves the API (api/route.py). `load` takes --cohort and --course for a
school's own PDP files (paths or https links), --replace to rebuild, and --config for another pipeline file;
see api/load.py and docs/integration.md.
"""
from __future__ import annotations

import argparse
import logging
import sys

from api.load import LoadError, ensure_data_loaded


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
    parser.add_argument("--cohort", help="the school's PDP cohort file: a path or an https link")
    parser.add_argument("--course", help="the school's PDP course file: a path or an https link")
    parser.add_argument("--replace", action="store_true", help="rebuild the database even if it exists")
    parser.add_argument("--config", help="another pipeline file for the loader")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)

    if args.command in (None, "load"):
        # Only the options given, so a plain `python -m api load` keeps its old meaning.
        chosen = {"cohort": args.cohort, "course": args.course, "replace": args.replace, "config": args.config}
        try:
            ensure_data_loaded(**{name: value for name, value in chosen.items() if value})
        except LoadError as problem:
            sys.exit(f"python -m api load: {problem}")
    if args.command in (None, "serve"):
        serve(args.host, args.port)


if __name__ == "__main__":
    main()
