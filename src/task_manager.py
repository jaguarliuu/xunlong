"""异步任务管理系统"""

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
    """任务状态"""
    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


class TaskType(str, Enum):
    """任务类型"""
    REPORT = "report"
    FICTION = "fiction"
    PPT = "ppt"


@dataclass
class TaskInfo:
    """任务信息"""
    task_id: str
    task_type: TaskType
    status: TaskStatus
    query: str
    context: Dict[str, Any]

    # 时间戳
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # 进度和结果
    progress: int = 0  # 0-100
    current_step: str = ""
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    # 输出路径
    project_id: Optional[str] = None
    output_dir: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 转换枚举为字符串
        data['task_type'] = self.task_type.value
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskInfo':
        """从字典创建"""
        data['task_type'] = TaskType(data['task_type'])
        data['status'] = TaskStatus(data['status'])
        return cls(**data)


class TaskManager:
    """任务管理器"""

    def __init__(self, tasks_dir: str = "tasks"):
        """
        初始化任务管理器

        Args:
            tasks_dir: 任务数据存储目录
        """
        self.tasks_dir = Path(tasks_dir)
        self.tasks_dir.mkdir(exist_ok=True)
        logger.info(f"任务管理器初始化: {self.tasks_dir}")

    def _get_task_file(self, task_id: str) -> Path:
        """获取任务文件路径"""
        return self.tasks_dir / f"{task_id}.json"

    def create_task(
        self,
        task_type: TaskType,
        query: str,
        context: Dict[str, Any]
    ) -> str:
        """
        创建新任务

        Args:
            task_type: 任务类型
            query: 查询内容
            context: 任务上下文参数

        Returns:
            任务ID
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

        # 保存任务信息
        self._save_task(task_info)

        logger.info(f"创建任务: {task_id} ({task_type.value})")
        return task_id

    def _save_task(self, task_info: TaskInfo) -> None:
        """保存任务信息"""
        task_file = self._get_task_file(task_info.task_id)
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_info.to_dict(), f, ensure_ascii=False, indent=2)

    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """
        获取任务信息

        Args:
            task_id: 任务ID

        Returns:
            任务信息，不存在返回None
        """
        task_file = self._get_task_file(task_id)

        if not task_file.exists():
            return None

        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return TaskInfo.from_dict(data)
        except Exception as e:
            logger.error(f"读取任务失败 {task_id}: {e}")
            return None

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        **kwargs
    ) -> bool:
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 新状态
            **kwargs: 其他要更新的字段

        Returns:
            是否更新成功
        """
        task_info = self.get_task(task_id)
        if not task_info:
            return False

        # 更新状态
        task_info.status = status

        # 更新时间戳
        if status == TaskStatus.RUNNING and not task_info.started_at:
            task_info.started_at = datetime.now().isoformat()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            task_info.completed_at = datetime.now().isoformat()

        # 更新其他字段
        for key, value in kwargs.items():
            if hasattr(task_info, key):
                setattr(task_info, key, value)

        # 保存
        self._save_task(task_info)
        logger.info(f"任务状态更新 {task_id}: {status.value}")
        return True

    def update_task_progress(
        self,
        task_id: str,
        progress: int,
        current_step: str = ""
    ) -> bool:
        """
        更新任务进度

        Args:
            task_id: 任务ID
            progress: 进度(0-100)
            current_step: 当前步骤描述

        Returns:
            是否更新成功
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
        标记任务完成

        Args:
            task_id: 任务ID
            result: 任务结果
            project_id: 项目ID
            output_dir: 输出目录

        Returns:
            是否更新成功
        """
        return self.update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            progress=100,
            current_step="完成",
            result=result,
            project_id=project_id,
            output_dir=output_dir
        )

    def fail_task(self, task_id: str, error: str) -> bool:
        """
        标记任务失败

        Args:
            task_id: 任务ID
            error: 错误信息

        Returns:
            是否更新成功
        """
        return self.update_task_status(
            task_id,
            TaskStatus.FAILED,
            error=error
        )

    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            是否取消成功
        """
        task_info = self.get_task(task_id)
        if not task_info:
            return False

        # 只能取消待执行或运行中的任务
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
        列出任务

        Args:
            status: 筛选状态
            task_type: 筛选类型
            limit: 最大数量

        Returns:
            任务列表
        """
        tasks = []

        # 遍历所有任务文件
        for task_file in sorted(self.tasks_dir.glob("*.json"), reverse=True):
            if len(tasks) >= limit:
                break

            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                task_info = TaskInfo.from_dict(data)

                # 筛选
                if status and task_info.status != status:
                    continue
                if task_type and task_info.task_type != task_type:
                    continue

                tasks.append(task_info)
            except Exception as e:
                logger.error(f"读取任务文件失败 {task_file}: {e}")
                continue

        return tasks

    def get_pending_tasks(self, limit: int = 10) -> List[TaskInfo]:
        """获取待执行任务"""
        return self.list_tasks(status=TaskStatus.PENDING, limit=limit)

    def cleanup_old_tasks(self, days: int = 30) -> int:
        """
        清理旧任务

        Args:
            days: 保留天数

        Returns:
            清理数量
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
                    logger.info(f"清理旧任务: {data['task_id']}")
            except Exception as e:
                logger.error(f"清理任务失败 {task_file}: {e}")
                continue

        logger.info(f"清理完成: 删除 {cleaned} 个旧任务")
        return cleaned


# 全局任务管理器实例
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """获取全局任务管理器实例"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager
