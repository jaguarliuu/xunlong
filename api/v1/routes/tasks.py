"""
Task management endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Query, Depends
from loguru import logger

from api.v1.schemas.task import (
    ReportCreateRequest,
    FictionCreateRequest,
    PPTCreateRequest,
    TaskCreateResponse,
    TaskStatusResponse,
    TaskListResponse,
    TaskListItem,
    TaskProgressInfo,
    TaskResultInfo,
)
from api.v1.services.task_service import TaskService
from api.models.enums import TaskStatus, TaskType
from api.core.exceptions import TaskNotFoundException

router = APIRouter()


def get_task_service() -> TaskService:
    """Dependency injection for TaskService."""
    return TaskService()


@router.post("/report", response_model=TaskCreateResponse, status_code=201)
async def create_report_task(
    request: ReportCreateRequest,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Create a report generation task.

    This endpoint creates a new task for generating a research report based on the provided query.
    The task is queued for asynchronous processing by the worker.
    """
    logger.info(f"Creating report task: {request.query[:50]}")

    # Prepare extra metadata
    extra_metadata = {
        "report_type": request.report_type.value,
        "search_depth": request.search_depth.value,
        "max_results": request.max_results,
        "output_format": request.output_format.value,
        "template": request.template,
        "theme": request.theme,
    }

    # Create task
    task = task_service.create_task(
        task_type=TaskType.REPORT,
        query=request.query,
        extra_metadata=extra_metadata
    )

    return TaskCreateResponse(
        task_id=task.task_id,
        status=task.status,
        message="Report task created successfully"
    )


@router.post("/fiction", response_model=TaskCreateResponse, status_code=201)
async def create_fiction_task(
    request: FictionCreateRequest,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Create a fiction generation task.

    This endpoint creates a new task for generating a creative fiction story.
    """
    logger.info(f"Creating fiction task: {request.query[:50]}")

    # Prepare extra metadata
    extra_metadata = {
        "genre": request.genre.value,
        "length": request.length.value,
        "viewpoint": request.viewpoint.value,
        "constraints": request.constraints,
        "output_format": request.output_format.value,
        "template": request.template,
        "theme": request.theme,
    }

    # Create task
    task = task_service.create_task(
        task_type=TaskType.FICTION,
        query=request.query,
        extra_metadata=extra_metadata
    )

    return TaskCreateResponse(
        task_id=task.task_id,
        status=task.status,
        message="Fiction task created successfully"
    )


@router.post("/ppt", response_model=TaskCreateResponse, status_code=201)
async def create_ppt_task(
    request: PPTCreateRequest,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Create a presentation generation task.

    This endpoint creates a new task for generating a PowerPoint presentation.
    """
    logger.info(f"Creating PPT task: {request.query[:50]}")

    # Prepare extra metadata
    extra_metadata = {
        "target_slides": request.target_slides,
        "style": request.style.value,
        "theme": request.theme,
    }

    # Create task
    task = task_service.create_task(
        task_type=TaskType.PPT,
        query=request.query,
        extra_metadata=extra_metadata
    )

    return TaskCreateResponse(
        task_id=task.task_id,
        status=task.status,
        message="PPT task created successfully"
    )


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Get task status and progress.

    Returns detailed information about a task including its current status,
    progress, and results (if completed).
    """
    task = task_service.get_task(task_id)

    # Build progress info
    progress = TaskProgressInfo(
        percentage=task.metadata.progress_percentage,
        current_step=task.metadata.current_step,
        total_steps=task.metadata.total_steps,
        completed_steps=task.metadata.completed_steps
    )

    # Build result info (if completed)
    result = None
    if task.status == TaskStatus.COMPLETED:
        result = TaskResultInfo(
            output_files=task.metadata.output_files,
            project_path=task.metadata.project_path,
            extra=task.metadata.extra
        )

    return TaskStatusResponse(
        task_id=task.task_id,
        task_type=task.metadata.task_type,
        status=task.status,
        progress=progress,
        created_at=task.metadata.created_at,
        started_at=task.metadata.started_at,
        completed_at=task.metadata.completed_at,
        result=result,
        error=task.metadata.error_message
    )


@router.delete("/{task_id}", status_code=204)
async def cancel_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Cancel a task.

    Only pending or running tasks can be cancelled.
    Completed, failed, or already cancelled tasks cannot be cancelled.
    """
    task_service.cancel_task(task_id)
    logger.info(f"Task cancelled via API: {task_id}")


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    task_type: Optional[TaskType] = Query(None, description="Filter by task type"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    task_service: TaskService = Depends(get_task_service)
):
    """
    List tasks with optional filtering and pagination.

    Returns a paginated list of tasks matching the specified filters.
    """
    offset = (page - 1) * page_size
    tasks, total = task_service.list_tasks(
        status_filter=status,
        task_type_filter=task_type,
        limit=page_size,
        offset=offset
    )

    # Convert to list items
    task_items = [
        TaskListItem(
            task_id=task.task_id,
            task_type=task.metadata.task_type,
            status=task.status,
            query=task.metadata.query,
            created_at=task.metadata.created_at,
            progress_percentage=task.metadata.progress_percentage
        )
        for task in tasks
    ]

    return TaskListResponse(
        tasks=task_items,
        total=total,
        page=page,
        page_size=page_size
    )
