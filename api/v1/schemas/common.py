"""
Common schemas shared across endpoints.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy", description="Service health status")
    version: str = Field(description="API version")
    timestamp: str = Field(description="Current server timestamp")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(description="Error message")
    status_code: int = Field(description="HTTP status code")
    details: Optional[Any] = Field(default=None, description="Additional error details")


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit value."""
        return self.page_size
