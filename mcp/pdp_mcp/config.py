"""Settings, read from environment variables once at startup. See mcp/README.md for each one.

The access mode decides which tools the server registers. Only trusted configuration sets it: no
tool argument or chat message can change it while the server runs.

max_rows and query_timeout_seconds belong to the dormant query path, which no access mode
registers. They aren't read from the environment, so PDP_MCP_MAX_ROWS and
PDP_MCP_QUERY_TIMEOUT_SECONDS are ignored and can't stop the server. A mode that registers
execute_query would read them again.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

__all__ = ["REPO_ROOT", "ConfigError", "Settings", "from_env"]

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = REPO_ROOT / "normalized-data-model/output/pdp.sqlite"
ACCESS_MODES = ("definitions",)
RESERVED_MODES = {"aggregate": "it needs the Measures workstream's (#9) manifest and output contract, which "
                               "aren't agreed yet"}
BACKENDS = ("sqlite", "postgres")
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


class ConfigError(ValueError):
    """A setting is missing or wrong. The server doesn't start."""


@dataclass(frozen=True)
class Settings:
    access_mode: str = "definitions"
    backend: str | None = None   # no database: definitions mode doesn't need one
    sqlite_path: Path = DEFAULT_SQLITE_PATH
    postgres_url: str | None = field(default=None, repr=False)   # never printed: it can hold a password
    max_rows: int = 500                  # dormant query path only
    query_timeout_seconds: float = 30.0  # dormant query path only
    log_level: str = "WARNING"


def from_env(environ=None) -> Settings:
    env = os.environ if environ is None else environ
    access_mode = env.get("PDP_MCP_ACCESS_MODE", "").strip().lower() or "definitions"
    if access_mode in RESERVED_MODES:
        raise ConfigError(f"PDP_MCP_ACCESS_MODE={access_mode} isn't available yet: {RESERVED_MODES[access_mode]}. "
                          f"Unset PDP_MCP_ACCESS_MODE, or set it to definitions")
    if access_mode not in ACCESS_MODES:
        raise ConfigError(f"PDP_MCP_ACCESS_MODE must be definitions, not {access_mode!r}")

    backend = env.get("PDP_MCP_BACKEND", "").strip().lower() or None
    if backend is not None and backend not in BACKENDS:
        raise ConfigError(f"PDP_MCP_BACKEND must be sqlite or postgres, not {backend!r}")

    sqlite_path = Path(env.get("PDP_MCP_SQLITE_PATH") or DEFAULT_SQLITE_PATH).expanduser()
    if not sqlite_path.is_absolute():
        sqlite_path = REPO_ROOT / sqlite_path   # clients start the server from anywhere: relative means the repo

    postgres_url = env.get("PDP_MCP_POSTGRES_URL") or None
    if backend == "postgres" and not postgres_url:
        raise ConfigError("PDP_MCP_BACKEND is postgres, but PDP_MCP_POSTGRES_URL isn't set")

    log_level = env.get("PDP_MCP_LOG_LEVEL", "WARNING").strip().upper()
    if log_level not in LOG_LEVELS:
        raise ConfigError(f"PDP_MCP_LOG_LEVEL must be one of {', '.join(LOG_LEVELS)}, not {log_level!r}")

    return Settings(access_mode=access_mode, backend=backend, sqlite_path=sqlite_path, postgres_url=postgres_url,
                    log_level=log_level)
