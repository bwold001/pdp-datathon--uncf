"""Run the data model's loader into the Playground's database, and read its tables back.

The loader is synchronous and takes a while, so a run goes to a worker thread and the request
returns at once; the UI polls the run's status. One run at a time: a load replaces every model
table, so two at once would race. Run status lives in this process, so it's lost on restart and
assumes one server worker; the loader's own summary.yaml is the lasting record, and is read back
for a run this process doesn't know.
"""

import asyncio
import logging
from datetime import UTC, datetime
from functools import cache
from typing import Any

import pdp_model
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

from . import uploads
from .schemas import RunRequest, RunStatus, SourceKind, TableRows, TableSummary

logger = logging.getLogger(__name__)

# Playground loads write their table files here, not to output/tables/, which other squads read.
TABLES_DIR = pdp_model.MODEL_DIR / "output/playground/tables"

_runs: dict[str, RunStatus] = {}
_active_run: str | None = None
_tasks: set[asyncio.Task[None]] = set()  # keeps each running task referenced until it ends


class RunRefused(Exception):
    """A run wasn't started; status_code is the HTTP status to answer with."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


@cache
def model_tables() -> tuple[str, ...]:
    """The data model's tables, in the order the loader fills them."""
    return tuple(pdp_model.table_names())


def start_run(request: RunRequest) -> RunStatus:
    """Start loading the chosen uploads in the background. Returns the run's first status."""
    global _active_run
    cohort = _upload_file(request.cohort_upload_id, "cohort")
    course = _upload_file(request.course_upload_id, "course")
    if _active_run is not None:
        raise RunRefused(409, f"Run {_active_run} is still loading. Wait for it to finish.")
    status = RunStatus(
        run_id=pdp_model.new_run_id(),
        status="running",
        cohort_upload_id=request.cohort_upload_id,
        course_upload_id=request.course_upload_id,
        started_at=datetime.now(UTC),
    )
    _runs[status.run_id] = status
    _active_run = status.run_id  # set before any await, so a second request sees it
    task = asyncio.create_task(_load(status, cohort, course))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    return status


def get_run(run_id: str) -> RunStatus | None:
    """A run's status: from this process if it started it, else from the loader's summary.yaml."""
    if run_id in _runs:
        return _runs[run_id]
    report = pdp_model.load_report(run_id) if run_id.replace("-", "").isalnum() else None
    if report is None:
        return None
    return RunStatus(
        run_id=run_id,
        status="succeeded" if report.get("status") == "loaded" else "failed",
        started_at=report.get("started_at"),
        finished_at=report.get("finished_at"),
        error=report.get("error"),
        summary=_short_summary(report),
    )


async def table_summaries(session: AsyncSession) -> list[TableSummary]:
    """Every model table with its row count; null for a table that isn't in the database yet."""
    existing = await _existing_tables(session)
    summaries = []
    for name in model_tables():
        count = None
        if name in existing:
            count = (await session.execute(text(f'SELECT COUNT(*) FROM "{name}"'))).scalar_one()
        summaries.append(TableSummary(name=name, row_count=count))
    return summaries


async def table_rows(
    session: AsyncSession, name: str, limit: int, offset: int = 0
) -> TableRows | None:
    """One page of a model table (name) in primary key order, or None if it hasn't been loaded."""
    if name not in await _existing_tables(session):
        return None
    connection = await session.connection()
    key = await connection.run_sync(
        lambda sync: inspect(sync).get_pk_constraint(name)["constrained_columns"]
    )
    # A fixed order keeps pages from repeating or skipping rows; "1" is the first column.
    order = ", ".join(f'"{column}"' for column in key) or "1"
    # Safe to put in the SQL: name comes from model_tables() and key from that table's schema.
    result = await session.execute(
        text(f'SELECT * FROM "{name}" ORDER BY {order} LIMIT :limit OFFSET :offset'),
        {"limit": limit, "offset": offset},
    )
    columns = list(result.keys())
    rows = [dict(row) for row in result.mappings()]
    return TableRows(name=name, columns=columns, rows=rows, limit=limit, offset=offset)


async def _load(status: RunStatus, cohort: str | None, course: str | None) -> None:
    """Run the loader in a worker thread and record how it ended."""
    global _active_run
    try:
        summary = await asyncio.to_thread(
            pdp_model.run_load,
            settings.DATABASE_URL,
            status.run_id,
            cohort=cohort,
            course=course,
            progress=status.progress.append,
            tables_dir=TABLES_DIR,
        )
        status.summary = _short_summary(summary)
        status.status = "succeeded"
    except pdp_model.ConfigError as error:
        _fail(status, "invalid_input", error)
    except Exception as error:  # the loader rolls back and raises RuntimeError; others are bugs
        if not isinstance(error, RuntimeError):
            logger.exception("Load run %s failed unexpectedly", status.run_id)
        _fail(status, "load_failed", error)
    finally:
        status.finished_at = datetime.now(UTC)
        _active_run = None


def _fail(status: RunStatus, kind: str, error: Exception) -> None:
    """Record a failed run, with the loader's summary when it wrote one."""
    status.status = "failed"
    status.error_kind = kind
    status.error = str(error)
    report = pdp_model.load_report(status.run_id)
    status.summary = _short_summary(report) if report else None


def _upload_file(upload_id: str | None, kind: SourceKind) -> str | None:
    """The stored file for an upload id, checked to be the right kind; None for no upload."""
    if upload_id is None:
        return None
    upload = uploads.get_upload(upload_id)
    if upload is None:
        raise RunRefused(404, f"No upload {upload_id!r}.")
    if upload.kind != kind:
        raise RunRefused(422, f"Upload {upload_id} is a {upload.kind} file, not a {kind} file.")
    return str(uploads.upload_path(upload))


def _short_summary(summary: dict[str, Any]) -> dict[str, Any]:
    """The summary without its per-row held_back list, which can run to thousands of entries.

    held_back_rows counts only the cohort and course files' rows. The repo's enrichment files
    cover the full mock data, so their rows for students outside an upload are expected.
    """
    short = {key: value for key, value in summary.items() if key != "held_back"}
    # The cohort and course files share the load's validation run; each enrichment file has its own.
    core_files = {
        name
        for name, counts in (summary.get("validation") or {}).items()
        if counts.get("run_id") == summary.get("run_id")
    }
    held_back = summary.get("held_back") or []
    short["held_back_rows"] = sum(row.get("source_file") in core_files for row in held_back)
    return short


async def _existing_tables(session: AsyncSession) -> set[str]:
    """The model tables that are in the database now."""
    connection = await session.connection()
    names = await connection.run_sync(lambda sync: inspect(sync).get_table_names())
    return set(names) & set(model_tables())
