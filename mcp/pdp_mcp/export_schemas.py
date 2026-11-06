"""Write schemas/tools.json from what the server lists, so the published contract is the server's.

Run from mcp/:  python -m pdp_mcp.export_schemas
tests/test_contracts.py fails if the committed file differs from what the server lists.
"""

import json
from pathlib import Path

import anyio
from mcp.client import Client

from .config import Settings
from .server import build_server

SCHEMAS = Path(__file__).resolve().parents[1] / "schemas" / "tools.json"


async def listed_tools(client) -> list[dict]:
    """The tools a connected client sees, as published: sorted by name, without empty fields."""
    tools = (await client.list_tools()).tools
    return sorted((t.model_dump(mode="json", by_alias=True, exclude_none=True) for t in tools),
                  key=lambda t: t["name"])


def render(tools: list[dict], access_mode: str = "definitions") -> str:
    return json.dumps({"status": "verified", "access_mode": access_mode, "tools": tools}, indent=2) + "\n"


async def _export() -> None:
    # The default settings, not the environment: the published contract is the default mode's.
    async with Client(build_server(Settings())) as client:
        SCHEMAS.parent.mkdir(exist_ok=True)
        SCHEMAS.write_text(render(await listed_tools(client)))


if __name__ == "__main__":
    anyio.run(_export)
    print(f"wrote {SCHEMAS}")
