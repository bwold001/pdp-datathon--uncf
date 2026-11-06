"""Alembic environment: runs migrations with the same settings and models as the app."""

import asyncio
from logging.config import fileConfig

import pdp_model
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app.core.config import settings
from app.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# The data model's loader owns these tables in the same database (/sandbox/pipeline), and drops and
# recreates them on every load, so autogenerate must not propose dropping or changing them.
DATA_MODEL_TABLES = frozenset(pdp_model.table_names())


def include_object(obj, name, type_, reflected, compare_to) -> bool:
    """Leave the data model's tables, and their columns, indexes and keys, out of migrations."""
    table = name if type_ == "table" else getattr(getattr(obj, "table", None), "name", None)
    return table not in DATA_MODEL_TABLES


def run_migrations_offline() -> None:
    """Emit SQL to stdout instead of running it (`alembic upgrade head --sql`)."""
    context.configure(
        url=settings.async_database_url,
        target_metadata=target_metadata,
        include_object=include_object,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        # SQLite can't ALTER most things in place; batch mode copies the table instead.
        render_as_batch=connection.dialect.name == "sqlite",
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = create_async_engine(settings.async_database_url, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_async_migrations())
