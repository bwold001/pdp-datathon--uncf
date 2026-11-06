"""Request and response shapes for the Sandbox pipeline: uploads, load runs and table previews."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

SourceKind = Literal["cohort", "course"]
RunState = Literal["running", "succeeded", "failed"]

DATA_NOTE = (
    "Loaded with the normalized data model's own pipeline. The shared mock data is synthetic: "
    "nothing built on it is a finding about real students or institutions."
)


class Upload(BaseModel):
    """One stored file, ready to be loaded as the cohort or course file."""

    upload_id: str
    kind: SourceKind
    filename: str = Field(description="The name the file was uploaded with.")
    size_bytes: int
    sha256: str
    uploaded_at: datetime
    unexpected_columns: list[str] = Field(
        default=[], description="Columns the mapping config doesn't read. The loader ignores them."
    )


class UploadList(BaseModel):
    """Every stored upload, newest first."""

    uploads: list[Upload]


class RunRequest(BaseModel):
    """Which uploads to load. A file left out is the repo's configured mock file."""

    cohort_upload_id: str | None = None
    course_upload_id: str | None = None


class RunStatus(BaseModel):
    """One load run: running, or how it ended."""

    run_id: str
    status: RunState
    cohort_upload_id: str | None = None
    course_upload_id: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    progress: list[str] = Field(default=[], description="One line per finished pipeline step.")
    error_kind: Literal["invalid_input", "load_failed"] | None = None
    error: str | None = None
    summary: dict[str, Any] | None = Field(
        default=None,
        description="The loader's summary.yaml, with held_back replaced by a held_back_rows count.",
    )
    note: str = DATA_NOTE


class TableSummary(BaseModel):
    """One model table and how many rows it holds; row_count is null before the first load."""

    name: str
    row_count: int | None


class TableList(BaseModel):
    """Every model table, in the order the loader fills them."""

    tables: list[TableSummary]
    note: str = DATA_NOTE


class TableRows(BaseModel):
    """One page of a model table's rows."""

    name: str
    columns: list[str]
    rows: list[dict[str, Any]]
    limit: int
    offset: int = 0
    note: str = DATA_NOTE
