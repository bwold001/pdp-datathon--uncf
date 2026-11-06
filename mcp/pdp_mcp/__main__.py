"""Run the server over stdio: python -m pdp_mcp (from mcp/), or python mcp/run_server.py.

Before serving, it checks the settings and the metadata files the tools read, and stops with exit
code 2 and a message on stderr if either is unusable. It needs no database. stdout is the MCP
protocol: nothing else is printed there.
"""

import logging
import sys

from .config import ConfigError, from_env
from .metadata import Metadata
from .server import build_server

log = logging.getLogger("pdp_mcp")


def startup_problem(metadata=None):
    """Why the server can't serve its metadata, or None."""
    problem, _ = (metadata or Metadata()).status()
    return problem


def main() -> None:
    try:
        settings = from_env()
    except ConfigError as exc:
        print(f"pdp-mcp: can't start: {exc}", file=sys.stderr)
        sys.exit(2)
    logging.basicConfig(stream=sys.stderr, level=settings.log_level, format="pdp-mcp %(levelname)s %(message)s")
    problem = startup_problem()
    if problem:
        print(f"pdp-mcp: can't start: {problem}", file=sys.stderr)
        sys.exit(2)
    log.info("access mode %s", settings.access_mode)
    build_server(settings).run("stdio")


if __name__ == "__main__":
    main()
