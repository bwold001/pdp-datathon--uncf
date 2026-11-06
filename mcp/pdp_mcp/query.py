"""What execute_query checks before a query reaches the database, and how values become JSON.

The statement check here is the first layer, for a clear early error. It is not what keeps the
database read-only: that's the database itself (see db.py). A query that slips past this check
still can't write.
"""

import base64
import json
import math
import re
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID

__all__ = ["QueryRejected", "check_statement", "first_word", "to_json"]

ALLOWED_FIRST_WORDS = {"select", "with", "values", "explain"}
_COMMENT = re.compile(r"\s*(--[^\n]*(\n|$)|/\*.*?\*/)", re.S)
_WORD = re.compile(r"\s*([A-Za-z_]+)")


class QueryRejected(ValueError):
    """The query isn't allowed. Nothing was sent to the database."""


def check_statement(sql: str) -> str:
    """Return the statement without a trailing semicolon, or raise QueryRejected."""
    rest = _skip_comments(sql)
    match = _WORD.match(rest)
    first = first_word(sql)
    if first not in ALLOWED_FIRST_WORDS:
        raise QueryRejected(f"only SELECT, WITH, VALUES and EXPLAIN queries are allowed, not {first.upper() or 'this'}")
    if first == "explain":
        after = _skip_comments(rest[match.end():])
        options = after[:after.find(")")] if after.startswith("(") else after[:8]
        if re.search(r"\banaly[sz]e\b", options, re.I):
            raise QueryRejected("EXPLAIN ANALYZE runs the query; use EXPLAIN without ANALYZE")
    return re.sub(r";\s*$", "", sql.rstrip())


def first_word(sql: str) -> str:
    """The statement's first keyword, lower case, after any comments."""
    match = _WORD.match(_skip_comments(sql))
    return match.group(1).lower() if match else ""


def _skip_comments(text):
    while True:
        match = _COMMENT.match(text)
        if not match:
            return text.lstrip()
        text = text[match.end():]


def to_json(value):
    """One result value as a JSON scalar: string, number, boolean or null."""
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)   # JSON has no NaN or Infinity
    if isinstance(value, Decimal):
        return float(value) if value.is_finite() else str(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray, memoryview)):
        return base64.b64encode(bytes(value)).decode("ascii")
    if isinstance(value, (timedelta, UUID)):
        return str(value)
    return json.dumps(value, default=str)   # PostgreSQL arrays, json and the rest: as JSON text
