"""Finds the datathon repository around Playground, so chat can use its shared code and skills.

The metadata-advisor skill (.agents/skills/) and the definitions library (mcp/pdp_mcp) live outside
server_application/. Chat loads them only when a request arrives, so the server still starts
when it is deployed without the rest of the repository.
"""

import sys
from functools import cache
from pathlib import Path


class RepoNotFound(RuntimeError):
    """server_application/ is not inside the datathon repository."""


@cache
def repo_root() -> Path:
    """The nearest folder above this file that holds normalized-data-model/."""
    for folder in Path(__file__).resolve().parents:
        if (folder / "normalized-data-model").is_dir():
            return folder
    raise RepoNotFound("Sandbox chat needs the datathon repository around Playground.")


def import_path(*folders: str) -> None:
    """Put repository folders on sys.path, so their top-level modules can be imported."""
    for folder in folders:
        path = str(repo_root() / folder)
        if path not in sys.path:
            sys.path.insert(0, path)
