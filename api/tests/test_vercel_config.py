"""Checks vercel.json: the API and the Explorer are wired to the right services, and the bundle keeps the data."""
from __future__ import annotations

import importlib
import json
import re
from fnmatch import fnmatch
from pathlib import Path

from fastapi import FastAPI

from api.route import PREFIX

REPO = Path(__file__).resolve().parents[2]
CONFIG = json.loads((REPO / "vercel.json").read_text(encoding="utf-8"))
SERVICES = CONFIG["services"]
BACKEND = SERVICES["backend"]
FRONTEND = SERVICES["frontend"]
EXPLORER_PAGES = REPO / "playground" / "client_application" / "src" / "app" / "(uncf-explorer)"


def service_for(path: str) -> str:
    """The service Vercel sends a path to: the first rewrite whose source matches wins."""
    for rewrite in CONFIG["rewrites"]:
        if re.fullmatch(rewrite["source"], path):
            return rewrite["destination"]["service"]
    raise AssertionError(f"no rewrite matches {path}")


def excluded_patterns() -> list[str]:
    """The backend's excludeFiles glob, split out of its {a,b,c} braces."""
    (settings,) = BACKEND["functions"].values()
    return settings["excludeFiles"].strip("{}").split(",")


def is_excluded(path: str) -> bool:
    """Whether a repo-relative file would be left out of the API's bundle."""
    return any(fnmatch(path, pattern) for pattern in excluded_patterns())


def test_backend_entrypoint_is_the_results_api() -> None:
    """The backend service serves our FastAPI app."""
    module_name, attribute = BACKEND["entrypoint"].split(":")
    app = getattr(importlib.import_module(module_name), attribute)
    assert isinstance(app, FastAPI)


def test_backend_function_key_is_the_entrypoint_file() -> None:
    """excludeFiles is keyed by the entrypoint's file, so it applies to the API."""
    module_name = BACKEND["entrypoint"].split(":")[0]
    assert list(BACKEND["functions"]) == [module_name.replace(".", "/") + ".py"]


def test_api_paths_go_to_the_backend() -> None:
    """Results API paths reach FastAPI, not Next.js."""
    assert service_for(f"{PREFIX}/results") == "backend"
    assert service_for(f"{PREFIX}/health") == "backend"


def test_pages_go_to_the_frontend() -> None:
    """Explorer pages and Next.js assets reach the frontend."""
    assert service_for("/uncf/paths") == "frontend"
    assert service_for("/_next/static/chunk.js") == "frontend"


def test_backend_build_loads_the_data() -> None:
    """Each deploy builds pdp.sqlite from the CSVs in data/raw/."""
    assert BACKEND["buildCommand"] == "python -m api load"


def test_frontend_calls_the_api_on_the_same_site() -> None:
    """The client is built to call the API on its own site."""
    # Same origin as the pages, so the browser needs no CORS and previews call their own API.
    assert "NEXT_PUBLIC_API_BASE_URL=/api/v1 " in FRONTEND["buildCommand"]
    assert PREFIX.startswith("/api/v1/")


def test_home_redirects_to_an_explorer_tab_that_exists() -> None:
    """/ opens a real Explorer tab, since we host only the Explorer."""
    (redirect,) = [r for r in CONFIG["redirects"] if r["source"] == "/"]
    assert (EXPLORER_PAGES / redirect["destination"].lstrip("/") / "page.tsx").exists()


def test_bundle_keeps_what_the_api_reads() -> None:
    """The API's code and pdp.sqlite stay in its bundle."""
    for path in ["normalized-data-model/output/pdp.sqlite", "api/route.py", "measures/run_measures.py"]:
        assert not is_excluded(path), path


def test_bundle_drops_the_frontend_and_raw_data() -> None:
    """Big files the API never reads stay out of its bundle."""
    for path in ["playground/client_application/node_modules/next/package.json", "data/raw/pdp_cohort_data.csv", "api/tests/test_results.py"]:
        assert is_excluded(path), path
