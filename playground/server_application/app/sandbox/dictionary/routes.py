"""Sandbox column dictionary endpoints: what each normalized data model column means."""

from fastapi import APIRouter, HTTPException

from . import service
from .schemas import ColumnDefinition, ColumnDefinitionList

router = APIRouter(prefix="/sandbox/dictionary", tags=["sandbox: dictionary"])


@router.get("/columns")
def list_columns(table: str | None = None, source_file: str | None = None) -> ColumnDefinitionList:
    """Every column definition, optionally only one table's or only those one source file fills."""
    return ColumnDefinitionList(columns=service.find(table, source_file))


@router.get("/columns/{table}/{column}")
def get_column(table: str, column: str) -> ColumnDefinition:
    """One normalized column's definition, its sources and how it's stored."""
    try:
        return service.get(table, column)
    except service.ColumnNotFound as error:
        raise HTTPException(404, error.message) from error
