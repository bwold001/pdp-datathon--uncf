"""Start the PDP MCP server over stdio. Point an MCP client at this file; no working directory needed.

    /path/to/repo/.venv/bin/python /path/to/repo/mcp/run_server.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pdp_mcp.__main__ import main  # noqa: E402

main()
