"""Vercel entrypoint for chat over the build-generated synthetic extract."""

import os
import sys
from pathlib import Path

from measures.run_measures import DEFAULT_DATABASE

SERVER_ROOT = Path(__file__).resolve().parent / "playground" / "server_application"
sys.path.insert(0, str(SERVER_ROOT))
# These defaults apply only to this dedicated deployment, never the local Playground.
os.environ.setdefault("APP_ENV", "production")
os.environ.setdefault("UNCF_CHAT_ENABLED", "true")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{DEFAULT_DATABASE}")

from app.chat.deployment import create_app  # noqa: E402

app = create_app()
