"""Request cancellation must await the synchronous worker's cleanup."""

import asyncio
from threading import Event

import pytest

from analytics.execution import check_cancelled, execution_scope, run_sync


def test_task_cancellation_waits_for_worker_cleanup():
    """Hold cleanup behind an event so an abandoned worker fails deterministically."""

    async def scenario():
        """Cancel an active worker and release cleanup only after checking the task."""
        loop = asyncio.get_running_loop()
        started, release_cleanup, finished = Event(), Event(), Event()
        cleanup_started = asyncio.Event()
        with execution_scope(5) as execution:

            def worker():
                """Honor cancellation, then wait for permission to finish cleanup."""
                try:
                    started.set()
                    assert execution.stopped.wait(5)
                    check_cancelled()
                finally:
                    loop.call_soon_threadsafe(cleanup_started.set)
                    assert release_cleanup.wait(5)
                    finished.set()

            task = asyncio.create_task(run_sync(worker))
            try:
                assert await asyncio.to_thread(started.wait, 5)
                task.cancel()
                await asyncio.wait_for(cleanup_started.wait(), 5)
                assert not task.done()
            finally:
                release_cleanup.set()
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(task, 5)
            assert finished.is_set()

    asyncio.run(scenario())
