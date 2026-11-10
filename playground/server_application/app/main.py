from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.db.session import engine
from app.sandbox.router import sandbox_router
from app.uncf import uncf_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Schema changes belong to Alembic; startup never creates tables.
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=settings.docs_path,
        redoc_url=None,
        # Hides the docs page's long Schemas list. Each endpoint still shows its own shapes.
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        lifespan=lifespan,
    )

    register_exception_handlers(app)

    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    if settings.SANDBOX_ENABLED:
        app.include_router(sandbox_router, prefix=settings.API_V1_PREFIX)
    app.include_router(uncf_router(), prefix=settings.API_V1_PREFIX)
    if settings.UNCF_CHAT_ENABLED:
        from api.analyses import get_service as default_service
        from api.analyses import router as analytics_router

        from app.chat.routes import chat
        from app.chat.routes import router as chat_router
        from app.services.analytics import get_service

        app.dependency_overrides[default_service] = get_service
        app.add_api_route(
            f"{settings.API_V1_PREFIX}/sandbox/chat/suggest",
            chat,
            methods=["POST"],
            include_in_schema=False,
        )
        app.include_router(analytics_router)
        app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
        app.include_router(
            chat_router, prefix=f"{settings.API_V1_PREFIX}/uncf", include_in_schema=False
        )

    return app


app = create_app()
