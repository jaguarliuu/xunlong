"""
API Server Launcher

Starts the FastAPI server using Uvicorn.
"""

import uvicorn
from loguru import logger

from api.core.config import get_settings


def main():
    """Launch the API server."""
    settings = get_settings()

    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        lambda msg: print(msg, end=""),
        format=settings.log_format,
        level=settings.log_level,
        colorize=True
    )

    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Server: {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Reload: {settings.reload}")

    # Start server
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
