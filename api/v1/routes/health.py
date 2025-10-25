"""
Health check endpoints.
"""

from datetime import datetime
from fastapi import APIRouter
from loguru import logger

from api.v1.schemas.common import HealthResponse
from api.core.config import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns service health status, version, and current timestamp.
    """
    settings = get_settings()

    response = HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.utcnow().isoformat()
    )

    logger.debug("Health check performed")
    return response


@router.get("/", response_model=dict)
async def root():
    """
    API root endpoint.

    Returns basic API information and available endpoints.
    """
    settings = get_settings()

    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "api_v1": settings.api_v1_prefix,
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }
