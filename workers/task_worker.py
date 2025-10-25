"""
Background Task Worker

Polls for pending tasks and executes them asynchronously.
"""

import asyncio
import signal
import traceback
from typing import Optional
from loguru import logger

from api.v1.services.task_service import TaskService
from api.models.task import Task
from api.models.enums import TaskStatus, TaskType
from api.core.config import get_settings


class TaskWorker:
    """
    Background worker for processing tasks.

    Polls the task queue for pending tasks and executes them using the
    appropriate agent/generator based on task type.
    """

    def __init__(
        self,
        task_service: Optional[TaskService] = None,
        poll_interval: Optional[float] = None
    ):
        """
        Initialize task worker.

        Args:
            task_service: Task service instance (creates new if None)
            poll_interval: Polling interval in seconds (uses settings if None)
        """
        settings = get_settings()

        self.task_service = task_service or TaskService()
        self.poll_interval = poll_interval or settings.worker_poll_interval
        self.running = False
        self.current_task: Optional[Task] = None

        logger.info(f"TaskWorker initialized (poll interval: {self.poll_interval}s)")

    async def start(self):
        """
        Start the worker.

        Continuously polls for pending tasks and processes them.
        """
        self.running = True
        logger.info("TaskWorker started")

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        while self.running:
            try:
                # Get next pending task
                pending_tasks = self.task_service.get_pending_tasks(limit=1)

                if pending_tasks:
                    task = pending_tasks[0]
                    await self._process_task(task)
                else:
                    # No tasks, wait before next poll
                    await asyncio.sleep(self.poll_interval)

            except Exception as e:
                logger.exception(f"Error in worker loop: {e}")
                await asyncio.sleep(self.poll_interval)

        logger.info("TaskWorker stopped")

    def stop(self):
        """Stop the worker gracefully."""
        logger.info("Stopping TaskWorker...")
        self.running = False

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.warning(f"Received signal {signum}, initiating graceful shutdown...")
        self.stop()

    async def _process_task(self, task: Task):
        """
        Process a single task.

        Args:
            task: Task to process
        """
        self.current_task = task
        task_id = task.task_id
        task_type = task.metadata.task_type

        logger.info(f"Processing task {task_id} (type: {task_type.value})")

        try:
            # Update status to running
            self.task_service.update_task_status(task_id, TaskStatus.RUNNING)

            # Route to appropriate handler
            if task_type == TaskType.REPORT:
                await self._execute_report_task(task)
            elif task_type == TaskType.FICTION:
                await self._execute_fiction_task(task)
            elif task_type == TaskType.PPT:
                await self._execute_ppt_task(task)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

        except Exception as e:
            # Task failed
            error_msg = str(e)
            error_trace = traceback.format_exc()
            logger.error(f"Task {task_id} failed: {error_msg}")
            logger.debug(f"Traceback:\n{error_trace}")

            self.task_service.fail_task(
                task_id=task_id,
                error=error_msg,
                traceback=error_trace
            )

        finally:
            self.current_task = None

    async def _execute_report_task(self, task: Task):
        """
        Execute a report generation task.

        Args:
            task: Report task to execute
        """
        task_id = task.task_id
        query = task.metadata.query
        extra = task.metadata.extra

        logger.info(f"Generating report for: {query[:50]}")

        # Update progress
        self.task_service.update_task_progress(
            task_id,
            percentage=10,
            current_step="Initializing report generation"
        )

        # TODO: Integrate with existing report generation agents
        # For now, this is a placeholder that will be implemented in the next step
        # The integration will connect to:
        # - src/agents/report/ modules
        # - src/deep_search_agent.py
        # - src/export/ modules

        logger.warning(
            f"Report generation not yet implemented for task {task_id}. "
            "This will be integrated with existing agents in the next phase."
        )

        # Placeholder completion
        await asyncio.sleep(2)  # Simulate work

        self.task_service.complete_task(
            task_id=task_id,
            output_files=[],
            project_path=None,
            extra_result={"status": "placeholder"}
        )

        logger.info(f"Report task {task_id} completed (placeholder)")

    async def _execute_fiction_task(self, task: Task):
        """
        Execute a fiction generation task.

        Args:
            task: Fiction task to execute
        """
        task_id = task.task_id
        query = task.metadata.query

        logger.info(f"Generating fiction for: {query[:50]}")

        # Update progress
        self.task_service.update_task_progress(
            task_id,
            percentage=10,
            current_step="Initializing fiction generation"
        )

        # TODO: Integrate with existing fiction generation agents
        # Will connect to src/agents/fiction/ modules

        logger.warning(
            f"Fiction generation not yet implemented for task {task_id}. "
            "This will be integrated with existing agents in the next phase."
        )

        # Placeholder completion
        await asyncio.sleep(2)

        self.task_service.complete_task(
            task_id=task_id,
            output_files=[],
            project_path=None,
            extra_result={"status": "placeholder"}
        )

        logger.info(f"Fiction task {task_id} completed (placeholder)")

    async def _execute_ppt_task(self, task: Task):
        """
        Execute a presentation generation task.

        Args:
            task: PPT task to execute
        """
        task_id = task.task_id
        query = task.metadata.query

        logger.info(f"Generating PPT for: {query[:50]}")

        # Update progress
        self.task_service.update_task_progress(
            task_id,
            percentage=10,
            current_step="Initializing PPT generation"
        )

        # TODO: Integrate with existing PPT generation agents
        # Will connect to src/agents/ppt/ modules

        logger.warning(
            f"PPT generation not yet implemented for task {task_id}. "
            "This will be integrated with existing agents in the next phase."
        )

        # Placeholder completion
        await asyncio.sleep(2)

        self.task_service.complete_task(
            task_id=task_id,
            output_files=[],
            project_path=None,
            extra_result={"status": "placeholder"}
        )

        logger.info(f"PPT task {task_id} completed (placeholder)")


async def main():
    """Main entry point for running the worker."""
    settings = get_settings()

    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        lambda msg: print(msg, end=""),
        format=settings.log_format,
        level=settings.log_level,
        colorize=True
    )

    # Create and start worker
    worker = TaskWorker()
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
