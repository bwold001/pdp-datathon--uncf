"""Read-only access to the database, SQLite or PostgreSQL.

Only what differs between the two is here: how to connect read-only, how to list and describe
tables, and how to run one query with a time limit. Each call opens its own connection and closes
it, so a database that goes away and comes back needs no restart.

Read-only is enforced by the database, whatever the SQL says:
- SQLite: the file is opened with mode=ro and PRAGMA query_only, and while a query runs an
  authorizer allows only reads and functions, and denies a few functions by name.
- PostgreSQL: the session defaults to read-only transactions, every call runs in a READ ONLY
  transaction, and the transaction is always rolled back.
"""

import logging
import sqlite3
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass

from .query import first_word, to_json

__all__ = ["Unavailable", "Rejected", "Failed", "TimedOut", "Relation", "Described", "Result", "backend_for"]

log = logging.getLogger(__name__)


class Unavailable(RuntimeError):
    """The database can't be reached or opened. The message never holds credentials."""


class Rejected(RuntimeError):
    """The database refused the query as not read-only, or as more than one statement. Nothing ran."""


class Failed(RuntimeError):
    """The database couldn't run the query: bad SQL, an unknown column, a wrong parameter count."""

    def __init__(self, message, sqlstate=None):
        super().__init__(message)
        self.sqlstate = sqlstate


class TimedOut(RuntimeError):
    """The query ran past the time limit and was stopped."""


@dataclass
class Relation:
    name: str
    type: str   # table or view


@dataclass
class Described:
    columns: list   # [{name, data_type, nullable, primary_key}]
    primary_key: list
    foreign_keys: list   # [{columns, references_table, references_columns}]
    unique_constraints: list


@dataclass
class Result:
    columns: list   # [{name, data_type}]
    rows: list
    truncated: bool


def backend_for(settings):
    return SQLiteBackend(settings) if settings.backend == "sqlite" else PostgresBackend(settings)


class SQLiteBackend:
    engine = "sqlite"
    param_style = "qmark"
    schema_name = "main"
    # Actions a query may take. Everything else (writes, DDL, ATTACH, PRAGMA, transactions) is denied.
    ALLOWED_ACTIONS = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
    # Functions that reach outside the database, if the SQLite build has them.
    DENIED_FUNCTIONS = {"load_extension", "readfile", "writefile", "edit", "fts3_tokenizer"}
    PROGRESS_STEPS = 10_000   # check the clock every this many virtual machine instructions

    def __init__(self, settings):
        self.path = settings.sqlite_path

    @property
    def database_name(self):
        return self.path.name

    @contextmanager
    def connect(self):
        if not self.path.is_file():
            raise Unavailable(f"the SQLite database {self.path.name} doesn't exist. Load it first "
                              f"(normalized-data-model/README.md, 'Load the data'), or set PDP_MCP_SQLITE_PATH")
        try:
            # mode=ro: never creates or changes the file. isolation_level=None: no implicit BEGIN.
            connection = sqlite3.connect(f"{self.path.as_uri()}?mode=ro", uri=True, isolation_level=None)
            connection.execute("PRAGMA query_only = ON")
        except sqlite3.Error as exc:
            raise Unavailable(f"can't open the SQLite database {self.path.name}: {exc}") from None
        try:
            yield connection
        finally:
            connection.close()

    def server_version(self, connection):
        return sqlite3.sqlite_version

    def ping(self, connection):
        connection.execute("SELECT 1").fetchone()

    def relations(self, connection):
        rows = connection.execute("SELECT name, type FROM sqlite_schema WHERE type IN ('table', 'view') "
                                  "AND name NOT LIKE 'sqlite\\_%' ESCAPE '\\'").fetchall()
        return [Relation(name, type_) for name, type_ in rows]

    def describe(self, connection, relation):
        info = connection.execute("SELECT * FROM pragma_table_info(?)", (relation.name,)).fetchall()
        pk = [row[1] for row in sorted((r for r in info if r[5]), key=lambda r: r[5])]
        # An INTEGER PRIMARY KEY is the rowid: never null, though it isn't declared NOT NULL.
        rowid = pk[0] if len(pk) == 1 and next(r[2] for r in info if r[1] == pk[0]).upper() == "INTEGER" else None
        columns = [{"name": name, "data_type": type_, "nullable": not notnull and name != rowid,
                    "primary_key": name in pk}
                   for _, name, type_, notnull, _, _ in info]
        keys = defaultdict(list)
        for id_, _, table, from_, to in connection.execute("SELECT id, seq, \"table\", \"from\", \"to\" "
                                                           "FROM pragma_foreign_key_list(?) ORDER BY id, seq",
                                                           (relation.name,)):
            keys[id_].append((table, from_, to))
        foreign_keys = []
        for parts in keys.values():
            target = parts[0][0]
            to = [p[2] for p in parts]
            if None in to:   # REFERENCES t with no columns means t's primary key
                to = [r[1] for r in sorted((r for r in connection.execute("SELECT * FROM pragma_table_info(?)",
                                                                          (target,)) if r[5]), key=lambda r: r[5])]
            foreign_keys.append({"columns": [p[1] for p in parts], "references_table": target,
                                 "references_columns": to})
        unique = [[r[2] for r in connection.execute("SELECT * FROM pragma_index_info(?)", (name,))]
                  for _, name, is_unique, origin, _ in
                  connection.execute("SELECT * FROM pragma_index_list(?)", (relation.name,)).fetchall()
                  if is_unique and origin == "u"]
        return Described(columns, pk if relation.type == "table" else [], foreign_keys, sorted(unique))

    def warnings(self, connection, model_tables):
        return []

    def execute(self, sql, params, max_rows, timeout):
        with self.connect() as connection:
            denied = []

            def authorize(action, arg1, arg2, database, source):
                if action == sqlite3.SQLITE_FUNCTION:
                    if (arg2 or "").lower() in self.DENIED_FUNCTIONS:
                        denied.append(f"the function {arg2}()")
                        return sqlite3.SQLITE_DENY
                    return sqlite3.SQLITE_OK
                if action in self.ALLOWED_ACTIONS:
                    return sqlite3.SQLITE_OK
                denied.append(_SQLITE_ACTIONS.get(action, f"action {action}"))
                return sqlite3.SQLITE_DENY

            deadline = time.monotonic() + timeout
            connection.set_authorizer(authorize)
            connection.set_progress_handler(lambda: time.monotonic() > deadline, self.PROGRESS_STEPS)
            try:
                cursor = connection.execute(sql, params or ())
                rows = cursor.fetchmany(max_rows + 1)
            except (sqlite3.ProgrammingError, sqlite3.Warning) as exc:   # Python 3.10 and 3.11 raise Warning
                if "one statement" in str(exc):
                    raise Rejected("only one statement is allowed") from None
                raise Failed(str(exc)) from None
            except sqlite3.Error as exc:
                if denied:
                    raise Rejected(f"not allowed: {denied[0]}. Queries can only read") from None
                if time.monotonic() > deadline or "interrupted" in str(exc):
                    raise TimedOut() from None
                raise Failed(str(exc)) from None
            columns = [{"name": d[0], "data_type": None} for d in cursor.description or []]
            return Result(columns, [[to_json(v) for v in row] for row in rows[:max_rows]], len(rows) > max_rows)


# Names for the authorizer's action codes, for the error message. (Other SQLITE_ constants reuse the numbers.)
_SQLITE_ACTIONS = {getattr(sqlite3, f"SQLITE_{name}"): name.replace("_", " ") for name in (
    "CREATE_INDEX", "CREATE_TABLE", "CREATE_TEMP_INDEX", "CREATE_TEMP_TABLE", "CREATE_TEMP_TRIGGER",
    "CREATE_TEMP_VIEW", "CREATE_TRIGGER", "CREATE_VIEW", "DELETE", "DROP_INDEX", "DROP_TABLE", "DROP_TEMP_INDEX",
    "DROP_TEMP_TABLE", "DROP_TEMP_TRIGGER", "DROP_TEMP_VIEW", "DROP_TRIGGER", "DROP_VIEW", "INSERT", "PRAGMA",
    "TRANSACTION", "UPDATE", "ATTACH", "DETACH", "ALTER_TABLE", "REINDEX", "ANALYZE", "CREATE_VTABLE",
    "DROP_VTABLE", "SAVEPOINT")}


class PostgresBackend:
    engine = "postgres"
    param_style = "format"
    CONNECT_TIMEOUT = 10

    def __init__(self, settings):
        self.url = settings.postgres_url
        self.database_name = None
        self.schema_name = None

    @contextmanager
    def connect(self):
        import psycopg
        try:
            connection = psycopg.connect(self.url, connect_timeout=self.CONNECT_TIMEOUT, autocommit=True)
        except psycopg.Error as exc:
            log.warning("PostgreSQL connection failed: %s", exc)   # stderr only: it can name the host and user
            raise Unavailable(f"can't connect to PostgreSQL with PDP_MCP_POSTGRES_URL: {_connect_reason(exc)}") from None
        try:
            # Every transaction on this session is read-only, and so is each one below.
            connection.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
            connection.autocommit = False
            connection.read_only = True
            self.database_name, self.schema_name = connection.execute(
                "SELECT current_database(), current_schema()").fetchone()
            yield connection
        finally:
            try:
                connection.rollback()   # never commit
            finally:
                connection.close()

    def server_version(self, connection):
        return connection.execute("SHOW server_version").fetchone()[0].split(" ")[0]

    def ping(self, connection):
        connection.execute("SELECT 1").fetchone()

    def relations(self, connection):
        rows = connection.execute("SELECT c.relname, c.relkind FROM pg_class c "
                                  "JOIN pg_namespace n ON n.oid = c.relnamespace "
                                  "WHERE n.nspname = current_schema() AND c.relkind IN ('r', 'p', 'v')").fetchall()
        return [Relation(name, "view" if kind == "v" else "table") for name, kind in rows]

    def describe(self, connection, relation):
        columns = [{"name": name, "data_type": type_, "nullable": nullable, "primary_key": False}
                   for name, type_, nullable in connection.execute(
                       "SELECT a.attname, format_type(a.atttypid, a.atttypmod), NOT a.attnotnull "
                       "FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid "
                       "JOIN pg_namespace n ON n.oid = c.relnamespace "
                       "WHERE n.nspname = current_schema() AND c.relname = %s AND a.attnum > 0 "
                       "AND NOT a.attisdropped ORDER BY a.attnum", (relation.name,))]
        pk, foreign_keys, unique = [], [], []
        for kind, cols, target, target_cols in self._constraints(connection, relation.name):
            if kind == "p":
                pk = cols
            elif kind == "u":
                unique.append(cols)
            else:
                foreign_keys.append({"columns": cols, "references_table": target, "references_columns": target_cols})
        for column in columns:
            column["primary_key"] = column["name"] in pk
        return Described(columns, pk, foreign_keys, sorted(unique))

    def _constraints(self, connection, table):
        return connection.execute(
            "SELECT con.contype, "
            "ARRAY(SELECT a.attname FROM unnest(con.conkey) WITH ORDINALITY k(num, pos) "
            "      JOIN pg_attribute a ON a.attrelid = con.conrelid AND a.attnum = k.num ORDER BY k.pos), "
            "t.relname, "
            "ARRAY(SELECT a.attname FROM unnest(con.confkey) WITH ORDINALITY k(num, pos) "
            "      JOIN pg_attribute a ON a.attrelid = con.confrelid AND a.attnum = k.num ORDER BY k.pos) "
            "FROM pg_constraint con JOIN pg_class c ON c.oid = con.conrelid "
            "JOIN pg_namespace n ON n.oid = c.relnamespace LEFT JOIN pg_class t ON t.oid = con.confrelid "
            "WHERE n.nspname = current_schema() AND c.relname = %s AND con.contype IN ('p', 'u', 'f') "
            "ORDER BY con.conname", (table,)).fetchall()

    def warnings(self, connection, model_tables):
        found = []
        superuser, = connection.execute("SELECT rolsuper FROM pg_roles WHERE rolname = current_user").fetchone()
        if superuser:
            found.append("The PostgreSQL role is a superuser. Read-only transactions still stop writes, but a "
                         "superuser can read server files (pg_read_file). Connect as a SELECT-only role: "
                         "see mcp/README.md.")
        writable = [t for t, in connection.execute(
            "SELECT t FROM unnest(%s::text[]) t WHERE to_regclass(quote_ident(t)) IS NOT NULL AND "
            "has_table_privilege(to_regclass(quote_ident(t)), 'INSERT, UPDATE, DELETE, TRUNCATE')",
            (list(model_tables),))]
        if writable and not superuser:
            found.append(f"The PostgreSQL role can write {len(writable)} model tables, such as {writable[0]}. "
                         f"Read-only transactions stop it, but a SELECT-only role is safer: see mcp/README.md.")
        return found

    def execute(self, sql, params, max_rows, timeout):
        import psycopg
        from psycopg import errors

        with self.connect() as connection:
            connection.execute(f"SET LOCAL statement_timeout = {int(timeout * 1000)}")
            if params is None:
                # Passing parameters makes psycopg use the extended query protocol, which refuses a
                # second statement. With none of the caller's own, a literal % must be doubled.
                sql, params = sql.replace("%", "%%"), []
            # A server-side cursor reads only the rows asked for. EXPLAIN can't be declared as a cursor.
            explain = first_word(sql) == "explain"
            cursor = connection.cursor() if explain else connection.cursor(name="pdp_mcp_query")
            try:
                cursor.execute(sql, params)
                rows = cursor.fetchmany(max_rows + 1)
                description = cursor.description or []
            except errors.QueryCanceled:
                raise TimedOut() from None
            except (errors.ReadOnlySqlTransaction, errors.InsufficientPrivilege) as exc:
                raise Failed(_pg_message(exc), exc.sqlstate) from None
            except psycopg.errors.SyntaxError as exc:
                if "multiple commands" in str(exc):
                    raise Rejected("only one statement is allowed") from None
                raise Failed(_pg_message(exc), exc.sqlstate) from None
            except psycopg.ProgrammingError as exc:
                raise Failed(_pg_message(exc), getattr(exc, "sqlstate", None)) from None
            except psycopg.OperationalError as exc:
                if connection.closed:
                    raise Unavailable("the PostgreSQL connection was lost during the query") from None
                raise Failed(_pg_message(exc), exc.sqlstate) from None
            except psycopg.Error as exc:
                raise Failed(_pg_message(exc), exc.sqlstate) from None
            types = connection.adapters.types
            columns = [{"name": d.name, "data_type": (types.get(d.type_code).name if types.get(d.type_code) else None)}
                       for d in description]
            return Result(columns, [[to_json(v) for v in row] for row in rows[:max_rows]], len(rows) > max_rows)


def _pg_message(exc):
    diag = getattr(exc, "diag", None)
    return (diag.message_primary if diag and diag.message_primary else str(exc)).strip()


def _connect_reason(exc):
    """Why a connection failed, without the host, user or password libpq puts in its message."""
    text = str(exc).lower()
    for clue, reason in (("password authentication failed", "the user name or password was refused"),
                         ("no password supplied", "the URL has no password and the server wants one"),
                         ("does not exist", "the database or role doesn't exist"),
                         ("timeout", "the server didn't answer in time"),
                         ("connection refused", "nothing is listening at that host and port; is PostgreSQL running?"),
                         ("could not translate host name", "the host name couldn't be found"),
                         ("invalid", "the URL isn't a valid connection string")):
        if clue in text:
            return reason
    return "see the server's log (stderr) for details"
