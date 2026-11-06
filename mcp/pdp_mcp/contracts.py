"""The tool contracts: what each tool takes and returns.

These models are the one definition. server.py registers the tools with them, and
export_schemas.py writes schemas/tools.json from what the running server lists, so the published
schemas can't drift from the server. docs/tool-contracts.md explains them for people.

ExecuteQueryResult describes the dormant query path (db.py, query.py): it's kept and tested, but no
access mode registers a tool that returns it.

Changing a field here changes the contract for every workstream that calls the server. Say why,
and who it affects, in the pull request.
"""

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "AccessMode", "Engine", "ModelType", "ErrorCode", "Scalar", "TOOL_DESCRIPTIONS",
    "ErrorInfo", "ErrorResult",
    "TableSummary", "ListTablesResult",
    "ColumnInfo", "ForeignKey", "IncomingReference", "DescribeTableResult",
    "ResultColumn", "ExecuteQueryResult",
    "ColumnRef", "SourceRef", "SourceColumnDefinition", "NormalizedColumnDefinition",
    "ColumnDefinitionQuery", "ColumnDefinitionResult",
    "MetadataFile", "MetadataStatus", "ModelTables", "DatabaseStatus", "DatabaseInfoResult",
]

AccessMode = Literal["definitions"]   # aggregate is reserved: it waits for the Measures (#9) contract
Engine = Literal["sqlite", "postgres"]
ModelType = Literal["str", "int", "float", "bool", "date", "datetime"]
ErrorCode = Literal["invalid_argument", "not_found", "query_rejected", "query_failed", "timeout",
                    "database_unavailable", "internal_error"]
Scalar = Union[str, int, float, bool, None]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


# Errors: every tool returns this, with isError true, when it can't do what was asked.

class ErrorInfo(_Model):
    code: ErrorCode = Field(description="What kind of failure. Stable: callers can branch on it.")
    message: str = Field(description="What went wrong, for a person or a model to read. Never holds credentials.")
    details: dict[str, Any] | None = Field(
        default=None, description="Extra facts for this code, such as `suggestions` for not_found.")


class ErrorResult(_Model):
    error: ErrorInfo


# list_tables

class TableSummary(_Model):
    name: str
    type: Literal["table", "view"]
    in_model: bool = Field(description="True if the table is in the normalized model (destination_schema.yaml).")
    description: str | None = Field(
        description="What one row is, from the model's README. Blank for tables and views outside the model.")


class ListTablesResult(_Model):
    source: str = Field(description="The repo file the tables come from: the model's destination_schema.yaml. "
                                    "Tables a database adds outside the model, and views, aren't listed.")
    tables: list[TableSummary] = Field(description="Tables first, then views, each sorted by name.")


# describe_table

class ColumnInfo(_Model):
    name: str
    data_type: str | None = Field(
        description="The type a database declares, such as TEXT or BIGINT. Null in definitions mode: the "
                    "tables come from the model's schema, which has no engine types. Use model_type.")
    model_type: ModelType | None = Field(
        description="The model's type for this column, the same in every engine. Blank outside the model.")
    nullable: bool
    primary_key: bool


class ForeignKey(_Model):
    columns: list[str]
    references_table: str
    references_columns: list[str]


class IncomingReference(_Model):
    table: str = Field(description="The table whose foreign key points at this one.")
    columns: list[str] = Field(description="That table's columns.")
    references_columns: list[str] = Field(description="The columns of this table they point at.")


class DescribeTableResult(_Model):
    name: str
    type: Literal["table", "view"]
    in_model: bool
    description: str | None
    columns: list[ColumnInfo] = Field(description="In the table's column order.")
    primary_key: list[str] = Field(description="Empty if there is none, as for every view.")
    foreign_keys: list[ForeignKey] = Field(description="In the order of their first column in the table.")
    referenced_by: list[IncomingReference] = Field(description="Sorted by table, then columns.")
    unique_constraints: list[list[str]] = Field(description="Each group of columns that is unique together.")


# execute_query: dormant. Kept and tested, but no access mode registers it as a tool.

class ResultColumn(_Model):
    name: str
    data_type: str | None = Field(
        description="The database's type for the result column where it reports one. SQLite often doesn't.")


class ExecuteQueryResult(_Model):
    columns: list[ResultColumn]
    rows: list[list[Scalar]] = Field(
        description="One array per row, in column order. Dates and timestamps are ISO 8601 strings.")
    row_count: int = Field(description="The rows returned here, at most max_rows.")
    truncated: bool = Field(description="True if the query had more rows than max_rows. The rest weren't read.")
    max_rows: int = Field(description="The limit used for this call.")
    elapsed_ms: float


# get_column_definition

class ColumnRef(_Model):
    table: str
    column: str


class SourceRef(_Model):
    source_file: str
    source_column: str
    dictionary_name: str | None
    description: str | None


class SourceColumnDefinition(_Model):
    kind: Literal["source"] = Field(description="A column of a raw input file.")
    source_file: str = Field(description="Such as pdp_cohort_data.csv, or an enrichment file.")
    source_column: str = Field(description="The column name as the file writes it.")
    dictionary_name: str | None = Field(description="The data dictionary's name for it. Blank if it has none.")
    description: str | None = Field(
        description="From data/dictionaries/column_lookup.csv. Blank if the lookup has none: never made up.")
    dictionary_file: str | None = Field(
        description="The markdown dictionary with the full entry, repo-relative. Blank for enrichment files.")
    destinations: list[ColumnRef] = Field(description="Where the loader stores it. Empty if it's dropped.")
    missing_values: list[str] = Field(description="Codes the file writes for no value. A blank cell always is one.")
    unknown_values: list[str] = Field(description="Codes the file writes for unknown. Stored as UNKNOWN in text columns.")
    value_map: dict[str, str] = Field(
        description="Values this file writes its own way, and what is stored instead, from its mapping config. "
                    "Fixes for known mock-data bugs aren't here: they're in config/data_fixes.yaml.")


class NormalizedColumnDefinition(_Model):
    kind: Literal["normalized"] = Field(description="A column of a table in the normalized model.")
    table: str
    column: str
    description: str | None = Field(
        description="The description of its source column, when all its sources agree. Blank otherwise: "
                    "read sources[].description.")
    model_type: ModelType
    nullable: bool
    primary_key: bool
    foreign_key: str | None = Field(description="`table.column` it points at.")
    unique_group: str | None = Field(description="Columns sharing a group name are unique together.")
    default_value: str | None = Field(description="Stored when the source gives no value.")
    unknown_value: str | None = Field(description="Stored when the source says it doesn't know.")
    allowed_values: list[str] | None = Field(
        description="The codes an `error` or `warning` rule allows, from enum or value_set rules. "
                    "Blank if no rule lists them.")
    rules: list[dict[str, Any]] = Field(description="The validation rules, as written in destination_schema.yaml.")
    sources: list[SourceRef] = Field(description="The source columns the loader fills it from. Empty if it's generated.")


class ColumnDefinitionQuery(_Model):
    column: str
    table: str | None
    source_file: str | None


class ColumnDefinitionResult(_Model):
    query: ColumnDefinitionQuery = Field(description="The arguments, echoed back.")
    matches: list[Annotated[Union[SourceColumnDefinition, NormalizedColumnDefinition],
                            Field(discriminator="kind")]] = Field(
        description="Every match, source columns first. Never empty: no match is a not_found error.")


# get_database_info

class MetadataFile(_Model):
    path: str = Field(description="Repo-relative.")
    sha256: str | None = Field(description="Its SHA-256, so two consumers can tell they read the same file. "
                                           "Blank if it can't be read.")


class MetadataStatus(_Model):
    healthy: bool = Field(description="True if every metadata file was read and parsed.")
    error: ErrorInfo | None = Field(description="Why not. Blank when healthy.")
    files: list[MetadataFile] = Field(description="The repo files the metadata tools read.")
    table_count: int = Field(description="Tables in the model's schema.")


class ModelTables(_Model):
    expected: list[str] = Field(description="The tables in destination_schema.yaml.")
    missing: list[str] = Field(description="Expected tables the database doesn't have.")


class DatabaseStatus(_Model):
    engine: Engine
    healthy: bool = Field(description="True if the database answered a query just now.")
    error: ErrorInfo | None = Field(description="Why it isn't healthy. Blank when healthy.")
    server_version: str | None
    database: str | None = Field(
        description="The SQLite file name or the PostgreSQL database name. Never a path, host, user or password.")
    database_schema: str | None
    model_tables: ModelTables
    table_count: int | None
    view_count: int | None


class DatabaseInfoResult(_Model):
    access_mode: AccessMode = Field(
        description="What this server may expose, set by trusted configuration at startup. `definitions`: "
                    "metadata only, no data-query tools, no student-level values.")
    capabilities: list[str] = Field(description="The tools this server registered for its access mode.")
    read_only: Literal[True] = Field(description="Always true: the server never writes.")
    metadata: MetadataStatus
    database: DatabaseStatus | None = Field(
        description="The database named by PDP_MCP_BACKEND, if one is set. No tool in definitions mode reads "
                    "it: this only reports whether it's reachable. Null when none is configured.")
    warnings: list[str] = Field(description="Problems worth knowing, such as a PostgreSQL role that can write.")


TOOL_DESCRIPTIONS = {
    "list_tables": (
        "List the tables of the normalized PDP data model, with what one row of each is. Start here. "
        "Read from the model's schema, not a database: no student data."
    ),
    "describe_table": (
        "Describe one table of the normalized model: its columns with types and nullability, its primary key, "
        "its foreign keys, its unique groups, and the tables that point at it. From the model's schema."
    ),
    "get_column_definition": (
        "Look up what a column means. Takes a raw file column (such as Retention or Student_GUID) or a "
        "normalized table column (such as cohort_membership.retention), and returns its data dictionary "
        "description, type, allowed codes, and where it comes from or goes to. Never invents a definition."
    ),
    "get_database_info": (
        "Say what this server exposes and whether it's healthy: the access mode, its tools, the metadata files "
        "it reads, and, if one is configured, whether the database is reachable. Never returns credentials."
    ),
}
