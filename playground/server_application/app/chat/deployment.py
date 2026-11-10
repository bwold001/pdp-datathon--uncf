"""Host only chat and its read-only analytics dependencies, without Sandbox or uploads."""

from api.analyses import get_service as standalone_service
from fastapi import FastAPI

from app.chat.routes import router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.services.analytics import get_service


def create_app() -> FastAPI:
    """Mount the canonical chat route and its existing compatibility alias."""
    app = FastAPI(title="Student success chat", docs_url=None, redoc_url=None, openapi_url=None)
    register_exception_handlers(app)
    app.dependency_overrides[standalone_service] = get_service
    if settings.UNCF_CHAT_ENABLED:
        app.include_router(router, prefix="/api/v1")
        app.include_router(router, prefix="/api/v1/uncf", include_in_schema=False)
    return app
