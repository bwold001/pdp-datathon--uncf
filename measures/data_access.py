"""Dependency-free read interfaces shared by calculation owners and runtime adapters."""

from typing import Any, Protocol


class ReadConnection(Protocol):
    """Execute trusted owner-defined SQL without owning transaction lifetime."""

    def execute(self, sql: str, parameters=()) -> Any:
        """Execute a fixed query and return its cursor."""
        ...

    def cursor(self) -> Any:
        """Create a cursor with this view's declared row representation."""
        ...


class ReadSnapshot(Protocol):
    """Expose independent row views of one caller-owned transaction."""

    named: ReadConnection
    positional: ReadConnection
