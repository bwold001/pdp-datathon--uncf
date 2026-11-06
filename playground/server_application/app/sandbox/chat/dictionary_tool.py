"""The get_column_dictionary tool: the /sandbox/dictionary endpoint's definitions, for the model.

It adds what get_column_definition doesn't say: how the model stores each column (type, unknown
value, allowed codes) next to the PDP dictionary's codes and the raw columns that fill it.
"""

from typing import Any

from app.sandbox.dictionary import service
from app.sandbox.dictionary.schemas import ColumnDefinitionList

from .metadata_tools import ToolError, error_body

NAME = "get_column_dictionary"

TOOL = {
    "name": NAME,
    "description": (
        "The Playground's column dictionary for one normalized table, or one column of it: the PDP "
        "dictionary's description and codes, the raw file columns that fill it, and how the model "
        "stores it (type, nullable, unknown value, allowed codes). Use it for the codes to filter "
        "or group on before writing a query."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "table": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128,
                "description": "A table name from list_tables, such as cohort_membership.",
            },
            "column": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128,
                "description": "One column of that table. Leave out for every column.",
            },
        },
        "required": ["table"],
    },
}


def call(arguments: dict[str, Any]) -> dict[str, Any]:
    """One column's dictionary entry, or every entry for a table. Raises ToolError."""
    table, column = arguments["table"], arguments.get("column")
    if column:
        try:
            return service.get(table, column).model_dump(mode="json")
        except service.ColumnNotFound as error:
            raise ToolError(error_body("not_found", error.message)) from None
    columns = service.find(table)
    if not columns:
        message = f"{table} has no dictionary entries. list_tables has the model's tables."
        raise ToolError(error_body("not_found", message))
    return ColumnDefinitionList(columns=columns).model_dump(mode="json")
