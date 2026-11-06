"""Every sandbox page's endpoints. main.py mounts this only when SANDBOX_ENABLED."""

from fastapi import APIRouter

from app.sandbox.add_a_sandbox_page import routes as add_a_sandbox_page
from app.sandbox.chart_examples import routes as chart_examples
from app.sandbox.chat import routes as chat
from app.sandbox.dictionary import routes as dictionary
from app.sandbox.kpi_examples import routes as kpi_examples
from app.sandbox.measures import routes as measures
from app.sandbox.pipeline import routes as pipeline

sandbox_router = APIRouter(tags=["sandbox"])
sandbox_router.include_router(chart_examples.router)
sandbox_router.include_router(dictionary.router)
sandbox_router.include_router(measures.router)
sandbox_router.include_router(chat.router)
sandbox_router.include_router(kpi_examples.router)
sandbox_router.include_router(add_a_sandbox_page.router)
sandbox_router.include_router(pipeline.router)
