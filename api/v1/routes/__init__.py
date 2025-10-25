"""
API route definitions.
"""

from fastapi import APIRouter
from api.v1.routes import health, tasks

# Create main router for v1
router = APIRouter()

# Include sub-routers
router.include_router(health.router, tags=["Health"])
router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

__all__ = ["router"]
