"""
Task Worker Launcher

Starts the background task worker for processing asynchronous tasks.
"""

import asyncio
from loguru import logger

from workers.task_worker import TaskWorker
from api.core.config import get_settings


async def main():
    """Launch the task worker."""
    settings = get_settings()

    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        lambda msg: print(msg, end=""),
        format=settings.log_format,
        level=settings.log_level,
        colorize=True
    )

    logger.info(f"Starting XunLong Task Worker")
    logger.info(f"Poll interval: {settings.worker_poll_interval}s")
    logger.info(f"Max retries: {settings.worker_max_retries}")

    # Create and start worker
    worker = TaskWorker()
    await worker.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
