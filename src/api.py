"""REST API - """

import json
from typing import Optional, Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger

from .config import DeepSearchConfig
from .pipeline import DeepSearchPipeline
from .models import SearchResult
from .task_manager import get_task_manager, TaskType, TaskStatus


# Pydantic
class ReportRequest(BaseModel):
    """TODO: Add docstring."""
    query: str = Field(..., description="")
    report_type: str = Field("comprehensive", description=": comprehensive/daily/analysis/research")
    search_depth: str = Field("deep", description=": surface/medium/deep")
    max_results: int = Field(20, description="")
    output_format: str = Field("html", description=": html/md")
    html_template: str = Field("academic", description="HTML: academic/technical")
    html_theme: str = Field("light", description="HTML: light/dark")


class FictionRequest(BaseModel):
    """TODO: Add docstring."""
    query: str = Field(..., description="")
    genre: str = Field("mystery", description=": mystery/scifi/fantasy/horror/romance/wuxia")
    length: str = Field("short", description=": short/medium/long")
    viewpoint: str = Field("first", description=": first/third/omniscient")
    constraints: List[str] = Field(default_factory=list, description="")
    output_format: str = Field("html", description=": html/md")
    html_template: str = Field("novel", description="HTML")
    html_theme: str = Field("sepia", description="HTML")


class PPTRequest(BaseModel):
    """PPT"""
    query: str = Field(..., description="PPT")
    slides: int = Field(15, description="")
    style: str = Field("business", description=": business/creative/minimal/educational")
    theme: str = Field("corporate-blue", description="")


class TaskResponse(BaseModel):
    """TODO: Add docstring."""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """TODO: Add docstring."""
    task_id: str
    task_type: str
    status: str
    progress: int
    current_step: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# FastAPI
app = FastAPI(
    title="XunLong API",
    description="AIAPI - PPT",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 
task_manager = get_task_manager()

# 
config = DeepSearchConfig()
pipeline = DeepSearchPipeline(config)


@app.get("/")
async def root():
    """TODO: Add docstring."""
    return {
        "name": "XunLong API",
        "version": "1.0.0",
        "description": "AIAPI",
        "features": ["", "", "PPT"],
        "endpoints": {
            "async_tasks": {
                "create_report": "POST /api/v1/tasks/report",
                "create_fiction": "POST /api/v1/tasks/fiction",
                "create_ppt": "POST /api/v1/tasks/ppt",
                "get_status": "GET /api/v1/tasks/{task_id}",
                "get_result": "GET /api/v1/tasks/{task_id}/result",
                "download_file": "GET /api/v1/tasks/{task_id}/download",
                "cancel_task": "DELETE /api/v1/tasks/{task_id}",
                "list_tasks": "GET /api/v1/tasks"
            },
            "legacy": {
                "search": "GET /search"
            }
        }
    }


@app.get("/health")
async def health_check():
    """TODO: Add docstring."""
    return {
        "status": "healthy",
        "task_manager": "ok",
        "version": "1.0.0"
    }


# ============================================================
# API
# ============================================================

@app.post("/api/v1/tasks/report", response_model=TaskResponse)
async def create_report_task(request: ReportRequest):
    """
    

    IDID
    """
    try:
        # 
        context = {
            'output_type': 'report',
            'report_type': request.report_type,
            'search_depth': request.search_depth,
            'max_results': request.max_results,
            'output_format': request.output_format,
            'html_template': request.html_template,
            'html_theme': request.html_theme
        }

        # 
        task_id = task_manager.create_task(
            task_type=TaskType.REPORT,
            query=request.query,
            context=context
        )

        logger.info(f": {task_id}")

        return TaskResponse(
            task_id=task_id,
            status="pending",
            message=f"ID: {task_id}"
        )

    except Exception as e:
        logger.error(f": {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/tasks/fiction", response_model=TaskResponse)
async def create_fiction_task(request: FictionRequest):
    """
    

    IDID
    """
    try:
        # 
        context = {
            'output_type': 'fiction',
            'genre': request.genre,
            'length': request.length,
            'viewpoint': request.viewpoint,
            'constraints': request.constraints,
            'output_format': request.output_format,
            'html_template': request.html_template,
            'html_theme': request.html_theme
        }

        # 
        task_id = task_manager.create_task(
            task_type=TaskType.FICTION,
            query=request.query,
            context=context
        )

        logger.info(f": {task_id}")

        return TaskResponse(
            task_id=task_id,
            status="pending",
            message=f"ID: {task_id}"
        )

    except Exception as e:
        logger.error(f": {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/tasks/ppt", response_model=TaskResponse)
async def create_ppt_task(request: PPTRequest):
    """
    PPT

    IDID
    """
    try:
        # 
        context = {
            'output_type': 'ppt',
            'slides': request.slides,
            'style': request.style,
            'theme': request.theme
        }

        # 
        task_id = task_manager.create_task(
            task_type=TaskType.PPT,
            query=request.query,
            context=context
        )

        logger.info(f"PPT: {task_id}")

        return TaskResponse(
            task_id=task_id,
            status="pending",
            message=f"PPTID: {task_id}"
        )

    except Exception as e:
        logger.error(f"PPT: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    

    
    """
    task_info = task_manager.get_task(task_id)

    if not task_info:
        raise HTTPException(status_code=404, detail=f": {task_id}")

    return TaskStatusResponse(
        task_id=task_info.task_id,
        task_type=task_info.task_type.value,
        status=task_info.status.value,
        progress=task_info.progress,
        current_step=task_info.current_step,
        created_at=task_info.created_at,
        started_at=task_info.started_at,
        completed_at=task_info.completed_at,
        result=task_info.result,
        error=task_info.error
    )


@app.get("/api/v1/tasks/{task_id}/result")
async def get_task_result(task_id: str):
    """
    

    
    """
    task_info = task_manager.get_task(task_id)

    if not task_info:
        raise HTTPException(status_code=404, detail=f": {task_id}")

    if task_info.status == TaskStatus.PENDING:
        raise HTTPException(status_code=400, detail="")

    if task_info.status == TaskStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail=f" ({task_info.progress}%)"
        )

    if task_info.status == TaskStatus.FAILED:
        raise HTTPException(
            status_code=500,
            detail=f": {task_info.error}"
        )

    if task_info.status == TaskStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="")

    # 
    return {
        "task_id": task_id,
        "status": "completed",
        "result": task_info.result,
        "project_id": task_info.project_id,
        "output_dir": task_info.output_dir
    }


@app.get("/api/v1/tasks/{task_id}/download")
async def download_task_file(
    task_id: str,
    file_type: str = Query("html", description=": html/md/pdf")
):
    """
    

    HTMLMarkdown
    """
    task_info = task_manager.get_task(task_id)

    if not task_info:
        raise HTTPException(status_code=404, detail=f": {task_id}")

    if task_info.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="")

    # 
    output_dir = Path(task_info.output_dir)

    # 
    if file_type == "html":
        file_path = output_dir / "reports" / "FINAL_REPORT.html"
    elif file_type == "md":
        file_path = output_dir / "reports" / "FINAL_REPORT.md"
    elif file_type == "pdf":
        file_path = output_dir / "exports" / "report.pdf"
    else:
        raise HTTPException(status_code=400, detail=f": {file_type}")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f": {file_type}")

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=file_path.name
    )


@app.delete("/api/v1/tasks/{task_id}")
async def cancel_task(task_id: str):
    """
    

    
    """
    success = task_manager.cancel_task(task_id)

    if not success:
        raise HTTPException(
            status_code=400,
            detail=""
        )

    return {
        "task_id": task_id,
        "status": "cancelled",
        "message": ""
    }


@app.get("/api/v1/tasks")
async def list_tasks(
    status: Optional[str] = Query(None, description=""),
    task_type: Optional[str] = Query(None, description=""),
    limit: int = Query(50, ge=1, le=200, description="")
):
    """
    

    
    """
    # 
    status_filter = TaskStatus(status) if status else None
    type_filter = TaskType(task_type) if task_type else None

    tasks = task_manager.list_tasks(
        status=status_filter,
        task_type=type_filter,
        limit=limit
    )

    return {
        "total": len(tasks),
        "tasks": [
            {
                "task_id": t.task_id,
                "task_type": t.task_type.value,
                "status": t.status.value,
                "query": t.query,
                "progress": t.progress,
                "created_at": t.created_at,
                "completed_at": t.completed_at
            }
            for t in tasks
        ]
    }


# ============================================================
# 
# ============================================================


@app.get("/search", response_model=SearchResult)
async def search_endpoint(
    q: str = Query(..., description=""),
    k: int = Query(5, ge=1, le=20, description=""),
    engine: str = Query("duckduckgo", description=""),
    headless: bool = Query(True, description="")
):
    """
    
    
    Args:
        q: 
        k:  (1-20)
        engine: 
        headless: 
        
    Returns:
        JSON
    """
    try:
        logger.info(f"API: {q} (topk={k}, engine={engine})")
        
        # 
        temp_config = DeepSearchConfig(
            headless=headless,
            search_engine=engine,
            topk=k
        )
        
        # 
        temp_pipeline = DeepSearchPipeline(temp_config)
        
        # 
        result = await temp_pipeline.search(q)
        
        logger.info(f"API: {result.success_count}/{result.total_found} ")
        return result
        
    except Exception as e:
        logger.error(f"API: {e}")
        raise HTTPException(status_code=500, detail=f": {str(e)}")


@app.get("/config")
async def get_config():
    """TODO: Add docstring."""
    return {
        "headless": config.headless,
        "search_engine": config.search_engine,
        "topk": config.topk,
        "shots_dir": config.shots_dir,
        "browser_timeout": config.browser_timeout,
        "page_wait_time": config.page_wait_time
    }


# 
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """TODO: Add docstring."""
    logger.error(f"API: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f": {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)