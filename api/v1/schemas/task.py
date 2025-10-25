"""
Task-related request and response schemas.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from api.models.enums import (
    TaskStatus,
    TaskType,
    ReportType,
    SearchDepth,
    OutputFormat,
    FictionGenre,
    FictionLength,
    FictionViewpoint,
    PPTStyle,
)


# ========== Request Schemas ==========

class ReportCreateRequest(BaseModel):
    """Request schema for creating a report generation task."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "AI技术发展趋势分析",
                "report_type": "comprehensive",
                "search_depth": "deep",
                "max_results": 20,
                "output_format": "html"
            }
        }
    )

    query: str = Field(description="Report topic or research question")
    report_type: ReportType = Field(
        default=ReportType.COMPREHENSIVE,
        description="Type of report to generate"
    )
    search_depth: SearchDepth = Field(
        default=SearchDepth.MEDIUM,
        description="Depth of web search"
    )
    max_results: int = Field(
        default=20,
        ge=5,
        le=100,
        description="Maximum search results to process"
    )
    output_format: OutputFormat = Field(
        default=OutputFormat.HTML,
        description="Output file format"
    )
    template: Optional[str] = Field(
        default=None,
        description="HTML template style (academic, technical, etc.)"
    )
    theme: Optional[str] = Field(
        default="light",
        description="Visual theme (light, dark)"
    )


class FictionCreateRequest(BaseModel):
    """Request schema for creating a fiction generation task."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "一个关于时间旅行的科幻故事",
                "genre": "scifi",
                "length": "medium",
                "viewpoint": "third",
                "output_format": "html"
            }
        }
    )

    query: str = Field(description="Fiction concept, plot, or theme")
    genre: FictionGenre = Field(
        default=FictionGenre.FANTASY,
        description="Fiction genre"
    )
    length: FictionLength = Field(
        default=FictionLength.MEDIUM,
        description="Target story length"
    )
    viewpoint: FictionViewpoint = Field(
        default=FictionViewpoint.THIRD_PERSON,
        description="Narrative viewpoint"
    )
    constraints: Optional[list[str]] = Field(
        default=None,
        description="Additional creative constraints or requirements"
    )
    output_format: OutputFormat = Field(
        default=OutputFormat.HTML,
        description="Output file format"
    )
    template: Optional[str] = Field(
        default="novel",
        description="HTML template style"
    )
    theme: Optional[str] = Field(
        default="sepia",
        description="Visual theme (sepia, light, dark)"
    )


class PPTCreateRequest(BaseModel):
    """Request schema for creating a presentation generation task."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "区块链技术商业应用",
                "target_slides": 15,
                "style": "business",
                "theme": "corporate-blue"
            }
        }
    )

    query: str = Field(description="Presentation topic")
    target_slides: int = Field(
        default=15,
        ge=5,
        le=50,
        description="Target number of slides"
    )
    style: PPTStyle = Field(
        default=PPTStyle.BUSINESS,
        description="Presentation style"
    )
    theme: str = Field(
        default="corporate-blue",
        description="Color theme"
    )


# ========== Response Schemas ==========

class TaskCreateResponse(BaseModel):
    """Response after creating a task."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "pending",
                "message": "Task created successfully"
            }
        }
    )

    task_id: str = Field(description="Unique task identifier")
    status: TaskStatus = Field(description="Initial task status")
    message: str = Field(description="Human-readable status message")


class TaskProgressInfo(BaseModel):
    """Task progress information."""

    percentage: int = Field(ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = Field(
        default=None,
        description="Current processing step"
    )
    total_steps: Optional[int] = Field(
        default=None,
        description="Total number of steps"
    )
    completed_steps: int = Field(default=0, description="Number of completed steps")


class TaskResultInfo(BaseModel):
    """Task result information."""

    output_files: list[str] = Field(
        default_factory=list,
        description="List of generated file paths"
    )
    project_path: Optional[str] = Field(
        default=None,
        description="Path to project directory"
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional result data"
    )


class TaskStatusResponse(BaseModel):
    """Detailed task status response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_type": "report",
                "status": "running",
                "progress": {
                    "percentage": 45,
                    "current_step": "Generating report outline",
                    "total_steps": 8,
                    "completed_steps": 3
                },
                "created_at": "2025-01-15T10:30:00Z",
                "started_at": "2025-01-15T10:30:05Z"
            }
        }
    )

    task_id: str = Field(description="Task identifier")
    task_type: TaskType = Field(description="Type of task")
    status: TaskStatus = Field(description="Current status")

    # Progress
    progress: TaskProgressInfo = Field(description="Progress information")

    # Timestamps
    created_at: datetime = Field(description="Task creation timestamp")
    started_at: Optional[datetime] = Field(
        default=None,
        description="Task start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Task completion timestamp"
    )

    # Results (only when completed)
    result: Optional[TaskResultInfo] = Field(
        default=None,
        description="Task results (available when completed)"
    )

    # Error info (only when failed)
    error: Optional[str] = Field(
        default=None,
        description="Error message (available when failed)"
    )


class TaskListItem(BaseModel):
    """Abbreviated task info for list responses."""

    task_id: str
    task_type: TaskType
    status: TaskStatus
    query: str
    created_at: datetime
    progress_percentage: int


class TaskListResponse(BaseModel):
    """Response for listing tasks."""

    tasks: list[TaskListItem] = Field(description="List of tasks")
    total: int = Field(description="Total number of tasks")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
