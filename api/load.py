"""Build the SQLite database the API and chat read, with the data model's loader.

    python -m api load                                   sample files, only if no database exists yet
    python -m api load --replace                         rebuild from the sample files
    python -m api load --cohort FILE --course FILE       a school's own PDP files; always rebuilds

FILE is a path or an https link. UNCF_COHORT_URL and UNCF_COURSE_URL work like --cohort and --course, for a
hosted build that can't take arguments (Vercel runs `python -m api load`). The database goes to UNCF_DATABASE
when it's set, otherwise to normalized-data-model/output/pdp.sqlite.

A school's files load with api/config/school_pipeline.yaml: the cohort and course files only, without the
sample's synthetic enrichment files. --config names another pipeline file.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from measures.run_measures import configured_database

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parents[1] / "normalized-data-model"
SCHOOL_PIPELINE = Path(__file__).resolve().parent / "config" / "school_pipeline.yaml"
DOWNLOAD_SECONDS = 300


class LoadError(Exception):
    """The files to load are missing or can't be read; the message says which and what to do."""


def ensure_data_loaded(
    cohort: str | None = None,
    course: str | None = None,
    replace: bool = False,
    config: str | None = None,
    environ: dict | None = None,
) -> bool:
    """Load the data the command asks for. Returns False when the sample database already exists and nothing changed."""
    environ = os.environ if environ is None else environ
    cohort = cohort or environ.get("UNCF_COHORT_URL") or None
    course = course or environ.get("UNCF_COURSE_URL") or None
    if bool(cohort) != bool(course):
        raise LoadError("Give both files: the cohort file and the course file (--cohort and --course).")
    target = configured_database()
    if cohort is None and target.exists() and not replace:
        logger.info("%s already exists; pass --replace to rebuild it", target)
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="uncf-load-") as folder:
        command = [sys.executable, "-m", "src.loader.load", "--sqlite_path", str(target)]
        if cohort is not None:
            command += [
                "--config", str(Path(config).resolve() if config else SCHOOL_PIPELINE),
                "--cohort", str(local_file(cohort, Path(folder), "cohort")),
                "--course", str(local_file(course, Path(folder), "course")),
            ]
        elif config:
            command += ["--config", str(Path(config).resolve())]
        subprocess.run(command, cwd=MODEL_DIR, check=True)
    return True


def local_file(location: str, folder: Path, kind: str) -> Path:
    """A path on this machine for one input file: the path itself, or an https link downloaded into folder."""
    if "://" not in location:
        path = Path(location).expanduser().resolve()
        if not path.is_file():
            raise LoadError(f"No {kind} file at {path}.")
        return path
    link = urlparse(location)
    if link.scheme != "https":
        raise LoadError(f"The {kind} link must start with https://.")
    # Keep the link's file extension, which tells the loader the format. Never log the link: it can hold a token.
    path = folder / f"{kind}{Path(link.path).suffix or '.csv'}"
    logger.info("downloading the %s file from %s", kind, link.hostname)
    try:
        with open_link(location) as response, path.open("wb") as out:
            shutil.copyfileobj(response, out)
    except OSError as error:
        raise LoadError(f"Couldn't download the {kind} file from {link.hostname}: {error.__class__.__name__}.") from error
    return path


class HttpsOnlyRedirects(urllib.request.HTTPRedirectHandler):
    """Follow a redirect only to another https address, so a file of student records never travels unencrypted."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """Refuse a redirect to http (or any other scheme) before it is requested."""
        target = urlparse(newurl)
        if target.scheme != "https":
            fp.close()
            raise LoadError(f"The link redirected to a non-https address ({target.hostname}), so the download stopped.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def open_link(location: str):
    """Open an https link, following only https redirects (urlopen alone would follow one to http)."""
    return urllib.request.build_opener(HttpsOnlyRedirects).open(location, timeout=DOWNLOAD_SECONDS)
