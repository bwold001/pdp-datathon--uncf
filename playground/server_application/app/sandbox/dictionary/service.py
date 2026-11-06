"""Join the data model's column dictionary to how its schema stores each column.

Both are repo files that change only with a commit, so they're read once per process.
"""

from functools import cache

import pdp_model

from .schemas import ColumnDefinition


class ColumnNotFound(Exception):
    """No definition for a column; the message says whether the model has the column at all."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@cache
def definitions() -> tuple[ColumnDefinition, ...]:
    """Every column definition, in the schema's table and column order."""
    return tuple(
        ColumnDefinition(**record, stored=pdp_model.schema_field(record["table"], record["column"]))
        for record in pdp_model.column_dictionary()
    )


def find(table: str | None = None, source_file: str | None = None) -> list[ColumnDefinition]:
    """The definitions of one table's columns, or of the columns one source file fills, or both."""
    return [
        d
        for d in definitions()
        if (table is None or d.table == table)
        and (source_file is None or any(s.source_file == source_file for s in d.sources))
    ]


def get(table: str, column: str) -> ColumnDefinition:
    """One column's definition. Raises ColumnNotFound."""
    for definition in definitions():
        if definition.table == table and definition.column == column:
            return definition
    if pdp_model.schema_field(table, column) is None:
        raise ColumnNotFound(f"{table}.{column} isn't a column of the data model.")
    raise ColumnNotFound(
        f"{table}.{column} has no dictionary entry: no cohort or course file column fills it."
    )
