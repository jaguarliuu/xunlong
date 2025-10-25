"""
FastAPI Application Entry Point

Main application factory and configuration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.core.config import get_settings
from api.core.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    ErrorHandlingMiddleware,
    PerformanceMiddleware,
)
from api.v1.routes import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.

    Handles startup and shutdown tasks.
    """
    # Startup
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Task storage: {settings.task_storage_dir}")
    logger.info(f"Content storage: {settings.storage_dir}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()

    # Create app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Multi-modal AI content generation API for reports, fiction, and presentations",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add middleware (order matters - first added is outermost)
    # 1. Error handling (outermost - catches all errors)
    app.add_middleware(ErrorHandlingMiddleware)

    # 2. Performance monitoring
    app.add_middleware(PerformanceMiddleware, slow_request_threshold=5.0)

    # 3. Logging
    app.add_middleware(LoggingMiddleware)

    # 4. Request ID
    app.add_middleware(RequestIDMiddleware)

    # 5. CORS (innermost - modifies actual response)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Include routers
    app.include_router(v1_router, prefix=settings.api_v1_prefix)

    logger.success(f"FastAPI application created successfully")
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
