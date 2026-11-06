"""Sandbox pipeline endpoints: upload a file, load uploads into the model, preview its tables."""

from typing import Annotated

from fastapi import APIRouter, Body, Form, HTTPException, Query, UploadFile, status

from app.api.dependencies import SessionDep
from app.core.config import settings

from . import service, uploads
from .schemas import RunRequest, RunStatus, SourceKind, TableList, TableRows, Upload, UploadList

router = APIRouter(prefix="/sandbox/pipeline", tags=["sandbox: pipeline"])


@router.post("/uploads", status_code=status.HTTP_201_CREATED)
def create_upload(kind: Annotated[SourceKind, Form()], file: UploadFile) -> Upload:
    """Store a cohort or course CSV for a later run. Refuses a file missing a mapped column."""
    # A plain def: FastAPI runs it in a worker thread, so the copy doesn't block other requests.
    try:
        return uploads.save_upload(
            kind, file.filename or "", file.file, settings.PIPELINE_UPLOAD_MAX_BYTES
        )
    except uploads.UploadError as error:
        raise HTTPException(error.status_code, error.message) from error


@router.get("/uploads")
def list_uploads() -> UploadList:
    """Every stored upload, newest first."""
    return UploadList(uploads=uploads.list_uploads())


@router.post("/runs", status_code=status.HTTP_202_ACCEPTED)
async def start_run(request: Annotated[RunRequest | None, Body()] = None) -> RunStatus:
    """Start loading the chosen uploads, or the repo's mock files, into the model's tables."""
    try:
        return service.start_run(request or RunRequest())
    except service.RunRefused as error:
        raise HTTPException(error.status_code, error.message) from error


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> RunStatus:
    """A run's status and, once it ends, the loader's summary."""
    run = service.get_run(run_id)
    if run is None:
        raise HTTPException(404, f"No run {run_id!r}.")
    return run


@router.get("/tables")
async def list_tables(session: SessionDep) -> TableList:
    """Every model table and its row count."""
    return TableList(tables=await service.table_summaries(session))


@router.get("/tables/{name}")
async def get_table(
    name: str,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TableRows:
    """One page of a model table's rows, in primary key order."""
    if name not in service.model_tables():
        raise HTTPException(404, f"{name!r} isn't a data model table.")
    rows = await service.table_rows(session, name, limit, offset)
    if rows is None:
        raise HTTPException(404, f"{name!r} hasn't been loaded yet. Start a run first.")
    return rows
