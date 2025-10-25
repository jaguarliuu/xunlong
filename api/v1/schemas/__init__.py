"""
Pydantic schemas for API request/response validation.
"""

from api.v1.schemas.task import (
    TaskCreateResponse,
    TaskStatusResponse,
    TaskListResponse,
    ReportCreateRequest,
    FictionCreateRequest,
    PPTCreateRequest,
)
from api.v1.schemas.common import HealthResponse, ErrorResponse

__all__ = [
    "TaskCreateResponse",
    "TaskStatusResponse",
    "TaskListResponse",
    "ReportCreateRequest",
    "FictionCreateRequest",
    "PPTCreateRequest",
    "HealthResponse",
    "ErrorResponse",
]
