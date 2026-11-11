"""Caller-owned, thread-confined read snapshots for existing deterministic calculation owners."""

import re
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import get_ident
from typing import Callable
from uuid import uuid4

from analytics.execution import CalculationCancelled, check_cancelled, statement_timeout_ms, watch_sqlite
from analytics.provenance import DataUnavailable, SnapshotIdentity, read_snapshot_identity

_PLACEHOLDER = re.compile(r"('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|--[^\n]*(?:\n|$)|/\*.*?\*/)|\?", re.S)


def _postgres_query(sql, parameters):
    """Translate fixed question-mark parameters while preserving quoted text and comments."""
    if not parameters:
        return sql
    escaped = sql.replace("%", "%%")
    return _PLACEHOLDER.sub(lambda match: match[1] if match[1] is not None else "%s", escaped)


class _Session:
    """Keep ownership, failure state and driver rules in one transaction-local object."""

    def __init__(self, raw, postgres):
        """Bind a raw connection to the worker that opened it."""
        self.raw = raw
        self.postgres = postgres
        self.thread = get_ident()
        self.active = True
        self.failed = False
        if postgres:
            import psycopg
            self.errors = (psycopg.Error,)
        else:
            self.errors = (sqlite3.Error,)

    def check(self):
        """Reject abandoned, failed or cross-thread work before touching the driver."""
        check_cancelled()
        if get_ident() != self.thread:
            raise DataUnavailable("A snapshot must stay on its owning thread.")
        if not self.active or self.failed:
            raise DataUnavailable("The read snapshot is closed or unusable.")

    def call(self, function, *args):
        """Poison the transaction on driver failure and expose only safe errors."""
        self.check()
        try:
            result = function(*args)
        except self.errors as error:
            self.failed = True
            check_cancelled()
            if getattr(error, "sqlstate", None) == "57014":
                raise CalculationCancelled("The database statement deadline was reached") from error
            raise DataUnavailable("The configured read snapshot is unavailable.") from error
        check_cancelled()
        return result

    def cursor(self, named):
        """Choose row representation per cursor without mutating a global row factory."""
        self.check()
        if self.postgres:
            from psycopg.rows import dict_row, tuple_row
            raw = self.call(lambda: self.raw.cursor(row_factory=dict_row if named else tuple_row))
        else:
            raw = self.call(self.raw.cursor)
            raw.row_factory = sqlite3.Row if named else None
        return ReadCursor(self, raw, named)


class ReadCursor:
    """Bound fetching and query execution to the lifetime of the parent read snapshot."""

    def __init__(self, session, raw, named):
        """Remember only cursor-local row behavior."""
        self._session, self._raw, self._named = session, raw, named

    def execute(self, sql, parameters=()):
        """Execute fixed owner SQL with the remaining request timeout on every PostgreSQL statement."""
        session = self._session
        session.check()
        if session.postgres:
            with session.raw.cursor() as control:
                session.call(control.execute, f"SET LOCAL statement_timeout = {statement_timeout_ms()}")
            sql = _postgres_query(sql, parameters)
        bindings = parameters or None if session.postgres else parameters
        session.call(self._raw.execute, sql, bindings)
        return self

    def fetchone(self):
        """Fetch one row and normalize named SQLite rows to a dictionary."""
        row = self._session.call(self._raw.fetchone)
        return dict(row) if self._named and row is not None else row

    def fetchall(self):
        """Fetch checked rows in the cursor's declared representation."""
        rows = self._session.call(self._raw.fetchall)
        return [dict(r) for r in rows] if self._named else rows

    def fetchmany(self, size=1000):
        """Bound callers that consume results in batches."""
        rows = self._session.call(self._raw.fetchmany, size)
        return [dict(r) for r in rows] if self._named else rows

    def __iter__(self):
        """Check cancellation between rows instead of yielding a raw driver iterator."""
        while (row := self.fetchone()) is not None:
            yield row

    def close(self):
        """Release this cursor without closing or committing its parent transaction."""
        if self._session.active:
            self._session.call(self._raw.close)


class ReadView:
    """Expose fixed SQL execution and cursors, with no transaction ownership methods."""

    def __init__(self, session, named):
        """Select named or positional row behavior for this borrowed view."""
        self._session, self._named = session, named

    def cursor(self):
        """Open a cursor with this view's declared row behavior."""
        return self._session.cursor(self._named)

    def execute(self, sql, parameters=()):
        """Execute a fixed query without changing transaction lifetime."""
        return self.cursor().execute(sql, parameters)


class Snapshot:
    """Share one transaction and its pinned safe identity across sequential steps."""

    def __init__(self, session, require_identity=True):
        """Create both row views before reading identity through the same transaction."""
        self.named = ReadView(session, True)
        self.positional = ReadView(session, False)
        self.identity = read_snapshot_identity(self.named) if require_identity else None


@contextmanager
def connection_snapshot(raw, *, postgres=False, require_identity=True):
    """Own setup, rollback and close exactly once, even when setup or identity reads fail."""
    detach = None
    session = _Session(raw, postgres)
    try:
        check_cancelled()
        if postgres:
            raw.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            raw.execute(f"SET LOCAL statement_timeout = {statement_timeout_ms()}")
        else:
            raw.execute("PRAGMA query_only = ON")
            raw.execute("BEGIN")
            detach = watch_sqlite(raw)
        yield Snapshot(session, require_identity)
    except session.errors as error:
        check_cancelled()
        raise DataUnavailable("The configured read snapshot is unavailable.") from error
    finally:
        session.active = False
        if detach is not None:
            detach()
        try:
            raw.rollback()
        except session.errors as error:
            raise DataUnavailable("The read snapshot could not finish transaction cleanup.") from error
        finally:
            try:
                raw.close()
            except session.errors as error:
                raise DataUnavailable("The read snapshot could not close its connection.") from error


@contextmanager
def sqlite_snapshot(database, *, require_identity=True):
    """Open only the explicitly selected existing file in read-only mode."""
    check_cancelled()
    if database is None:
        raise DataUnavailable("No snapshot source is configured.")
    try:
        raw = sqlite3.connect(f"{Path(database).resolve().as_uri()}?mode=ro", uri=True, timeout=statement_timeout_ms() / 1000)
    except (sqlite3.Error, OSError) as error:
        raise DataUnavailable("The configured snapshot source is unavailable.") from error
    with connection_snapshot(raw, require_identity=require_identity) as snapshot:
        yield snapshot


@dataclass(frozen=True)
class SnapshotStep:
    """Name one trusted internal callback; operation dispatch remains in the future facade."""

    step_id: str
    execute: Callable


@dataclass(frozen=True)
class SnapshotFailure:
    """Describe a bounded snapshot failure without raw database exceptions."""

    step_id: str | None
    code: str
    message: str


@dataclass(frozen=True)
class SnapshotBatch:
    """Hold staged internal results after cleanup; disclosure must precede any serialization."""

    completed: tuple
    not_executed: tuple[str, ...]
    failure: SnapshotFailure | None
    identity: SnapshotIdentity | None
    execution_id: str
    started_at: datetime
    completed_at: datetime


def run_snapshot_steps(factory, steps: tuple[SnapshotStep, ...]) -> SnapshotBatch:
    """Stop after interruption and return staged work only after the owner finishes cleanup."""
    if not 1 <= len(steps) <= 4 or len({s.step_id for s in steps}) != len(steps):
        raise ValueError("snapshot batch requires one to four unique step IDs")
    completed, failure, identity, current = [], None, None, None
    started, execution_id = datetime.now(timezone.utc), uuid4().hex
    try:
        with factory() as snapshot:
            identity = snapshot.identity
            for step in steps:
                current = step.step_id
                check_cancelled()
                result = step.execute(snapshot)
                check_cancelled()
                completed.append((current, result))
    except CalculationCancelled:
        failure = SnapshotFailure(current, "timeout", "The snapshot execution deadline was reached.")
    except DataUnavailable as error:
        failure = SnapshotFailure(current, error.code, str(error))
    remaining = tuple(s.step_id for s in steps[len(completed):] if s.step_id != current) if failure else ()
    return SnapshotBatch(tuple(completed), remaining, failure, identity, execution_id, started, datetime.now(timezone.utc))
