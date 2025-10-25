"""
Custom API Exceptions

Defines application-specific exceptions with proper HTTP status codes.
"""

from typing import Any, Optional


class APIException(Exception):
    """Base exception for all API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class TaskNotFoundException(APIException):
    """Raised when a task is not found."""

    def __init__(self, task_id: str):
        super().__init__(
            message=f"Task not found: {task_id}",
            status_code=404,
            details={"task_id": task_id}
        )


class TaskAlreadyExistsException(APIException):
    """Raised when attempting to create a task with an existing ID."""

    def __init__(self, task_id: str):
        super().__init__(
            message=f"Task already exists: {task_id}",
            status_code=409,
            details={"task_id": task_id}
        )


class InvalidTaskStateException(APIException):
    """Raised when a task operation is invalid for the current task state."""

    def __init__(self, task_id: str, current_state: str, operation: str):
        super().__init__(
            message=f"Cannot perform '{operation}' on task {task_id} in state '{current_state}'",
            status_code=400,
            details={
                "task_id": task_id,
                "current_state": current_state,
                "operation": operation
            }
        )


class ResourceNotFoundException(APIException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            status_code=404,
            details={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )


class ValidationException(APIException):
    """Raised when request validation fails."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=422,
            details=details
        )


class ServiceUnavailableException(APIException):
    """Raised when a required service is unavailable."""

    def __init__(self, service_name: str, reason: Optional[str] = None):
        message = f"Service unavailable: {service_name}"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message=message,
            status_code=503,
            details={
                "service_name": service_name,
                "reason": reason
            }
        )


class RateLimitException(APIException):
    """Raised when rate limit is exceeded."""

    def __init__(self, limit: int, window: str):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window}",
            status_code=429,
            details={
                "limit": limit,
                "window": window
            }
        )


class InternalServerException(APIException):
    """Raised for unexpected internal errors."""

    def __init__(self, message: str = "Internal server error", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=500,
            details=details
        )
