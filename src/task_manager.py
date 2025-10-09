"""TODO: Add docstring."""

import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from loguru import logger


class TaskStatus(str, Enum):
    """TODO: Add docstring."""
    PENDING = "pending"  # 
    RUNNING = "running"  # 
    COMPLETED = "completed"  # 
    FAILED = "failed"  # 
    CANCELLED = "cancelled"  # 


class TaskType(str, Enum):
    """TODO: Add docstring."""
    REPORT = "report"
    FICTION = "fiction"
    PPT = "ppt"


@dataclass
class TaskInfo:
    """TODO: Add docstring."""
    task_id: str
    task_type: TaskType
    status: TaskStatus
    query: str
    context: Dict[str, Any]

    # 
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # 
    progress: int = 0  # 0-100
    current_step: str = ""
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    # 
    project_id: Optional[str] = None
    output_dir: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        data = asdict(self)
        # 
        data['task_type'] = self.task_type.value
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskInfo':
        """TODO: Add docstring."""
        data['task_type'] = TaskType(data['task_type'])
        data['status'] = TaskStatus(data['status'])
        return cls(**data)


class TaskManager:
    """TODO: Add docstring."""

    def __init__(self, tasks_dir: str = "tasks"):
        """
        

        Args:
            tasks_dir: 
        """
        self.tasks_dir = Path(tasks_dir)
        self.tasks_dir.mkdir(exist_ok=True)
        logger.info(f": {self.tasks_dir}")

    def _get_task_file(self, task_id: str) -> Path:
        """TODO: Add docstring."""
        return self.tasks_dir / f"{task_id}.json"

    def create_task(
        self,
        task_type: TaskType,
        query: str,
        context: Dict[str, Any]
    ) -> str:
        """
        

        Args:
            task_type: 
            query: 
            context: 

        Returns:
            ID
        """
        task_id = str(uuid.uuid4())

        task_info = TaskInfo(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            query=query,
            context=context,
            created_at=datetime.now().isoformat()
        )

        # 
        self._save_task(task_info)

        logger.info(f": {task_id} ({task_type.value})")
        return task_id

    def _save_task(self, task_info: TaskInfo) -> None:
        """TODO: Add docstring."""
        task_file = self._get_task_file(task_info.task_id)
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_info.to_dict(), f, ensure_ascii=False, indent=2)

    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """
        

        Args:
            task_id: ID

        Returns:
            None
        """
        task_file = self._get_task_file(task_id)

        if not task_file.exists():
            return None

        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return TaskInfo.from_dict(data)
        except Exception as e:
            logger.error(f" {task_id}: {e}")
            return None

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        **kwargs
    ) -> bool:
        """
        

        Args:
            task_id: ID
            status: 
            **kwargs: 

        Returns:
            
        """
        task_info = self.get_task(task_id)
        if not task_info:
            return False

        # 
        task_info.status = status

        # 
        if status == TaskStatus.RUNNING and not task_info.started_at:
            task_info.started_at = datetime.now().isoformat()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            task_info.completed_at = datetime.now().isoformat()

        # 
        for key, value in kwargs.items():
            if hasattr(task_info, key):
                setattr(task_info, key, value)

        # 
        self._save_task(task_info)
        logger.info(f" {task_id}: {status.value}")
        return True

    def update_task_progress(
        self,
        task_id: str,
        progress: int,
        current_step: str = ""
    ) -> bool:
        """
        

        Args:
            task_id: ID
            progress: (0-100)
            current_step: 

        Returns:
            
        """
        return self.update_task_status(
            task_id,
            TaskStatus.RUNNING,
            progress=progress,
            current_step=current_step
        )

    def complete_task(
        self,
        task_id: str,
        result: Dict[str, Any],
        project_id: str,
        output_dir: str
    ) -> bool:
        """
        

        Args:
            task_id: ID
            result: 
            project_id: ID
            output_dir: 

        Returns:
            
        """
        return self.update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            progress=100,
            current_step="",
            result=result,
            project_id=project_id,
            output_dir=output_dir
        )

    def fail_task(self, task_id: str, error: str) -> bool:
        """
        

        Args:
            task_id: ID
            error: 

        Returns:
            
        """
        return self.update_task_status(
            task_id,
            TaskStatus.FAILED,
            error=error
        )

    def cancel_task(self, task_id: str) -> bool:
        """
        

        Args:
            task_id: ID

        Returns:
            
        """
        task_info = self.get_task(task_id)
        if not task_info:
            return False

        # 
        if task_info.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            return False

        return self.update_task_status(task_id, TaskStatus.CANCELLED)

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        limit: int = 100
    ) -> List[TaskInfo]:
        """
        

        Args:
            status: 
            task_type: 
            limit: 

        Returns:
            
        """
        tasks = []

        # 
        for task_file in sorted(self.tasks_dir.glob("*.json"), reverse=True):
            if len(tasks) >= limit:
                break

            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                task_info = TaskInfo.from_dict(data)

                # 
                if status and task_info.status != status:
                    continue
                if task_type and task_info.task_type != task_type:
                    continue

                tasks.append(task_info)
            except Exception as e:
                logger.error(f" {task_file}: {e}")
                continue

        return tasks

    def get_pending_tasks(self, limit: int = 10) -> List[TaskInfo]:
        """TODO: Add docstring."""
        return self.list_tasks(status=TaskStatus.PENDING, limit=limit)

    def cleanup_old_tasks(self, days: int = 30) -> int:
        """
        

        Args:
            days: 

        Returns:
            
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned = 0

        for task_file in self.tasks_dir.glob("*.json"):
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                created_at = datetime.fromisoformat(data['created_at'])

                if created_at < cutoff_date:
                    task_file.unlink()
                    cleaned += 1
                    logger.info(f": {data['task_id']}")
            except Exception as e:
                logger.error(f" {task_file}: {e}")
                continue

        logger.info(f":  {cleaned} ")
        return cleaned


# 
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """TODO: Add docstring."""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager
