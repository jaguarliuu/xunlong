"""
API Middleware

Includes request/response logging, error handling, and performance monitoring.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from api.core.exceptions import APIException


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Adds a unique request ID to each request for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Add to request state for access in route handlers
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs all incoming requests and outgoing responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request
        request_id = getattr(request.state, "request_id", "unknown")
        start_time = time.time()

        logger.info(
            f"Request started | {request.method} {request.url.path} | "
            f"Request-ID: {request_id}"
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Request completed | {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.3f}s | "
            f"Request-ID: {request_id}"
        )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Catches and formats all exceptions as JSON responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except APIException as exc:
            # Handle known API exceptions
            logger.warning(
                f"API Exception: {exc.message} | "
                f"Status: {exc.status_code} | "
                f"Path: {request.url.path}"
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.message,
                    "status_code": exc.status_code,
                    "details": exc.details
                }
            )
        except Exception as exc:
            # Handle unexpected exceptions
            logger.exception(
                f"Unhandled exception: {str(exc)} | Path: {request.url.path}"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "status_code": 500,
                    "details": {"message": str(exc)}
                }
            )


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Monitors request performance and logs slow requests."""

    def __init__(self, app, slow_request_threshold: float = 5.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Check if request was slow
        duration = time.time() - start_time
        if duration > self.slow_request_threshold:
            logger.warning(
                f"Slow request detected | {request.method} {request.url.path} | "
                f"Duration: {duration:.3f}s"
            )

        # Add performance header
        response.headers["X-Process-Time"] = f"{duration:.3f}"

        return response
