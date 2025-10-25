"""
Task management service layer.

Handles task creation, retrieval, updates, and persistence.
"""

import json
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime
from loguru import logger

from api.models.task import Task, TaskMetadata
from api.models.enums import TaskStatus, TaskType
from api.core.config import get_settings
from api.core.exceptions import (
    TaskNotFoundException,
    TaskAlreadyExistsException,
    InvalidTaskStateException,
)


class TaskService:
    """Service for managing tasks."""

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize task service.

        Args:
            storage_dir: Directory for storing task metadata (defaults to settings)
        """
        settings = get_settings()
        self.storage_dir = Path(storage_dir or settings.task_storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"TaskService initialized with storage: {self.storage_dir}")

    def _get_task_file_path(self, task_id: str) -> Path:
        """Get file path for a task."""
        return self.storage_dir / f"{task_id}.json"

    def _task_exists(self, task_id: str) -> bool:
        """Check if a task exists."""
        return self._get_task_file_path(task_id).exists()

    def _save_task(self, task: Task) -> None:
        """Persist task to disk."""
        task_file = self._get_task_file_path(task.task_id)
        try:
            # Ensure metadata.updated_at is set
            task.metadata.updated_at = datetime.utcnow()

            # Write to file with pretty formatting
            with open(task_file, "w", encoding="utf-8") as f:
                json.dump(
                    task.model_dump(mode="json"),
                    f,
                    indent=2,
                    ensure_ascii=False,
                    default=str
                )
            logger.debug(f"Task saved: {task.task_id}")
        except Exception as e:
            logger.error(f"Failed to save task {task.task_id}: {e}")
            raise

    def _load_task(self, task_id: str) -> Task:
        """Load task from disk."""
        task_file = self._get_task_file_path(task_id)
        if not task_file.exists():
            raise TaskNotFoundException(task_id)

        try:
            with open(task_file, "r", encoding="utf-8") as f:
                task_data = json.load(f)
            task = Task(**task_data)
            logger.debug(f"Task loaded: {task_id}")
            return task
        except Exception as e:
            logger.error(f"Failed to load task {task_id}: {e}")
            raise

    def create_task(
        self,
        task_type: TaskType,
        query: str,
        extra_metadata: Optional[dict] = None
    ) -> Task:
        """
        Create a new task.

        Args:
            task_type: Type of task to create
            query: User query or topic
            extra_metadata: Additional metadata to include

        Returns:
            Created task

        Raises:
            TaskAlreadyExistsException: If task_id already exists (very unlikely)
        """
        task_id = str(uuid.uuid4())

        # Ensure uniqueness (extremely unlikely to collide)
        if self._task_exists(task_id):
            raise TaskAlreadyExistsException(task_id)

        # Build metadata
        metadata = TaskMetadata(
            query=query,
            task_type=task_type,
            extra=extra_metadata or {}
        )

        # Create task
        task = Task(
            task_id=task_id,
            status=TaskStatus.PENDING,
            metadata=metadata
        )

        # Persist
        self._save_task(task)

        logger.info(
            f"Task created: {task_id} | Type: {task_type.value} | Query: {query[:50]}"
        )
        return task

    def get_task(self, task_id: str) -> Task:
        """
        Get task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task object

        Raises:
            TaskNotFoundException: If task not found
        """
        return self._load_task(task_id)

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        error_message: Optional[str] = None
    ) -> Task:
        """
        Update task status.

        Args:
            task_id: Task identifier
            status: New status
            error_message: Error message if status is FAILED

        Returns:
            Updated task
        """
        task = self.get_task(task_id)

        # Update status
        old_status = task.status
        task.status = status

        # Handle status-specific updates
        if status == TaskStatus.RUNNING and not task.metadata.started_at:
            task.metadata.started_at = datetime.utcnow()

        if status.is_terminal():
            task.metadata.completed_at = datetime.utcnow()
            if status == TaskStatus.COMPLETED:
                task.metadata.progress_percentage = 100

        if status == TaskStatus.FAILED and error_message:
            task.metadata.error_message = error_message

        # Save changes
        self._save_task(task)

        logger.info(f"Task {task_id} status updated: {old_status.value} -> {status.value}")
        return task

    def update_task_progress(
        self,
        task_id: str,
        percentage: int,
        current_step: Optional[str] = None,
        completed_steps: Optional[int] = None
    ) -> Task:
        """
        Update task progress.

        Args:
            task_id: Task identifier
            percentage: Progress percentage (0-100)
            current_step: Description of current step
            completed_steps: Number of completed steps

        Returns:
            Updated task
        """
        task = self.get_task(task_id)

        # Update progress
        task.metadata.progress_percentage = max(0, min(100, percentage))

        if current_step:
            task.metadata.current_step = current_step

        if completed_steps is not None:
            task.metadata.completed_steps = completed_steps

        # Save changes
        self._save_task(task)

        logger.debug(
            f"Task {task_id} progress updated: {percentage}% | Step: {current_step}"
        )
        return task

    def complete_task(
        self,
        task_id: str,
        output_files: Optional[list[str]] = None,
        project_path: Optional[str] = None,
        extra_result: Optional[dict] = None
    ) -> Task:
        """
        Mark task as completed.

        Args:
            task_id: Task identifier
            output_files: List of generated file paths
            project_path: Path to project directory
            extra_result: Additional result data

        Returns:
            Updated task
        """
        task = self.get_task(task_id)

        # Mark as completed
        task.mark_completed(output_files=output_files)

        # Update result info
        if project_path:
            task.metadata.project_path = project_path

        if extra_result:
            task.metadata.extra.update(extra_result)

        # Save changes
        self._save_task(task)

        logger.info(f"Task completed: {task_id}")
        return task

    def fail_task(
        self,
        task_id: str,
        error: str,
        traceback: Optional[str] = None
    ) -> Task:
        """
        Mark task as failed.

        Args:
            task_id: Task identifier
            error: Error message
            traceback: Error traceback

        Returns:
            Updated task
        """
        task = self.get_task(task_id)

        # Mark as failed
        task.mark_failed(error=error, traceback=traceback)

        # Increment retry count
        task.metadata.retry_count += 1

        # Save changes
        self._save_task(task)

        logger.error(f"Task failed: {task_id} | Error: {error}")
        return task

    def cancel_task(self, task_id: str) -> Task:
        """
        Cancel a task.

        Args:
            task_id: Task identifier

        Returns:
            Updated task

        Raises:
            InvalidTaskStateException: If task cannot be cancelled
        """
        task = self.get_task(task_id)

        # Check if cancellable
        if not task.can_be_cancelled():
            raise InvalidTaskStateException(
                task_id=task_id,
                current_state=task.status.value,
                operation="cancel"
            )

        # Mark as cancelled
        task.mark_cancelled()

        # Save changes
        self._save_task(task)

        logger.info(f"Task cancelled: {task_id}")
        return task

    def list_tasks(
        self,
        status_filter: Optional[TaskStatus] = None,
        task_type_filter: Optional[TaskType] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> tuple[list[Task], int]:
        """
        List tasks with optional filtering and pagination.

        Args:
            status_filter: Filter by status
            task_type_filter: Filter by task type
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip

        Returns:
            Tuple of (tasks, total_count)
        """
        # Get all task files
        task_files = sorted(
            self.storage_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True  # Newest first
        )

        # Load and filter tasks
        tasks = []
        for task_file in task_files:
            try:
                task_id = task_file.stem
                task = self._load_task(task_id)

                # Apply filters
                if status_filter and task.status != status_filter:
                    continue
                if task_type_filter and task.metadata.task_type != task_type_filter:
                    continue

                tasks.append(task)
            except Exception as e:
                logger.warning(f"Failed to load task from {task_file}: {e}")
                continue

        # Get total count before pagination
        total_count = len(tasks)

        # Apply pagination
        if offset > 0:
            tasks = tasks[offset:]
        if limit is not None:
            tasks = tasks[:limit]

        logger.debug(
            f"Listed {len(tasks)} tasks (total: {total_count}, "
            f"filters: status={status_filter}, type={task_type_filter})"
        )

        return tasks, total_count

    def delete_task(self, task_id: str) -> None:
        """
        Delete a task.

        Args:
            task_id: Task identifier

        Raises:
            TaskNotFoundException: If task not found
        """
        task_file = self._get_task_file_path(task_id)
        if not task_file.exists():
            raise TaskNotFoundException(task_id)

        task_file.unlink()
        logger.info(f"Task deleted: {task_id}")

    def get_pending_tasks(self, limit: Optional[int] = None) -> list[Task]:
        """
        Get pending tasks for worker processing.

        Args:
            limit: Maximum number of tasks to return

        Returns:
            List of pending tasks
        """
        tasks, _ = self.list_tasks(
            status_filter=TaskStatus.PENDING,
            limit=limit
        )
        return tasks
