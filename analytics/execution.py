"""Cooperative calculation deadlines with worker cleanup before timeout responses."""
from __future__ import annotations

import asyncio
import time
from contextlib import contextmanager
from contextvars import ContextVar, copy_context
from threading import Event, Lock


class CalculationCancelled(Exception):
    """The request deadline or explicit cancellation stopped a calculation."""


class Execution:
    """Share a deadline and safe interruption callbacks with calculation workers."""

    def __init__(self, seconds):
        """Start a monotonic budget that is unaffected by wall-clock changes."""
        self.deadline = time.monotonic() + seconds
        self.stopped = Event()
        self.lock = Lock()
        self.interrupts = set()

    def expired(self):
        """Whether cancellation or the deadline requires the worker to stop."""
        return self.stopped.is_set() or time.monotonic() >= self.deadline

    def cancel(self):
        """Interrupt SQLite safely from the request thread."""
        self.stopped.set()
        with self.lock:
            callbacks = list(self.interrupts)
        for callback in callbacks:
            try:
                callback()
            except Exception:
                # A connection may have finished and closed after the snapshot.
                pass


CURRENT: ContextVar[Execution | None] = ContextVar("calculation_execution", default=None)


@contextmanager
def execution_scope(seconds):
    """Make the request budget available to synchronous workers."""
    token = CURRENT.set(Execution(seconds))
    try:
        yield CURRENT.get()
    finally:
        CURRENT.reset(token)


def check_cancelled():
    """Stop before further database access or numerical processing."""
    current = CURRENT.get()
    if current is not None and current.expired():
        raise CalculationCancelled("The calculation deadline was reached")


def checked(values):
    """Bound Python-side counting loops as well as database queries."""
    for value in values:
        check_cancelled()
        yield value


def statement_timeout_ms():
    """PostgreSQL statements cannot outlive the remaining request budget."""
    check_cancelled()
    current = CURRENT.get()
    if current is None:
        return 10_000
    remaining = max(1, int((current.deadline - time.monotonic()) * 1000))
    return min(10_000, remaining)


def watch_sqlite(connection):
    """Attach VM-level cancellation and return a cleanup callback."""
    current = CURRENT.get()
    if current is None:
        return lambda: None
    check_cancelled()
    interrupt = connection.interrupt
    connection.set_progress_handler(lambda: int(current.expired()), 1000)
    with current.lock:
        current.interrupts.add(interrupt)

    def detach():
        """Rollback and close without the progress handler interrupting cleanup."""
        with current.lock:
            current.interrupts.discard(interrupt)
        connection.set_progress_handler(None, 0)

    return detach


async def run_sync(function, *arguments, check_completion=True):
    """Await worker termination, including database cleanup, before propagating cancellation."""
    def invoke():
        """Validate the budget before and after synchronous work."""
        check_cancelled()
        try:
            result = function(*arguments)
        except Exception:
            check_cancelled()
            raise
        if check_completion:
            check_cancelled()
        return result

    worker = asyncio.get_running_loop().run_in_executor(None, copy_context().run, invoke)
    try:
        return await asyncio.shield(worker)
    except asyncio.CancelledError:
        current = CURRENT.get()
        if current is not None:
            current.cancel()
        # Shield keeps cancellation from abandoning the worker's finally blocks.
        while True:
            try:
                await asyncio.shield(worker)
                break
            except asyncio.CancelledError:
                if worker.done():
                    break
            except Exception:
                break
        raise
