"""REST API接口模块 - 支持同步和异步任务"""

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


# Pydantic模型定义
class ReportRequest(BaseModel):
    """报告生成请求"""
    query: str = Field(..., description="查询主题")
    report_type: str = Field("comprehensive", description="报告类型: comprehensive/daily/analysis/research")
    search_depth: str = Field("deep", description="搜索深度: surface/medium/deep")
    max_results: int = Field(20, description="最大搜索结果数")
    output_format: str = Field("html", description="输出格式: html/md")
    html_template: str = Field("academic", description="HTML模板: academic/technical")
    html_theme: str = Field("light", description="HTML主题: light/dark")


class FictionRequest(BaseModel):
    """小说创作请求"""
    query: str = Field(..., description="小说主题或提示")
    genre: str = Field("mystery", description="体裁: mystery/scifi/fantasy/horror/romance/wuxia")
    length: str = Field("short", description="篇幅: short/medium/long")
    viewpoint: str = Field("first", description="视角: first/third/omniscient")
    constraints: List[str] = Field(default_factory=list, description="特殊约束")
    output_format: str = Field("html", description="输出格式: html/md")
    html_template: str = Field("novel", description="HTML模板")
    html_theme: str = Field("sepia", description="HTML主题")


class PPTRequest(BaseModel):
    """PPT生成请求"""
    query: str = Field(..., description="PPT主题")
    slides: int = Field(15, description="幻灯片数量")
    style: str = Field("business", description="风格: business/creative/minimal/educational")
    theme: str = Field("corporate-blue", description="主题")


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
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


# 创建FastAPI应用
app = FastAPI(
    title="XunLong API",
    description="AI驱动的多模态内容生成API - 支持报告生成、小说创作、PPT制作",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取任务管理器
task_manager = get_task_manager()

# 全局配置和管道
config = DeepSearchConfig()
pipeline = DeepSearchPipeline(config)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "XunLong API",
        "version": "1.0.0",
        "description": "AI驱动的多模态内容生成API",
        "features": ["报告生成", "小说创作", "PPT制作"],
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
    """健康检查"""
    return {
        "status": "healthy",
        "task_manager": "ok",
        "version": "1.0.0"
    }


# ============================================================
# 异步任务API端点
# ============================================================

@app.post("/api/v1/tasks/report", response_model=TaskResponse)
async def create_report_task(request: ReportRequest):
    """
    创建报告生成任务（异步）

    返回任务ID，可通过任务ID查询进度和结果
    """
    try:
        # 构建上下文
        context = {
            'output_type': 'report',
            'report_type': request.report_type,
            'search_depth': request.search_depth,
            'max_results': request.max_results,
            'output_format': request.output_format,
            'html_template': request.html_template,
            'html_theme': request.html_theme
        }

        # 创建任务
        task_id = task_manager.create_task(
            task_type=TaskType.REPORT,
            query=request.query,
            context=context
        )

        logger.info(f"创建报告任务: {task_id}")

        return TaskResponse(
            task_id=task_id,
            status="pending",
            message=f"报告生成任务已创建，任务ID: {task_id}"
        )

    except Exception as e:
        logger.error(f"创建报告任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/tasks/fiction", response_model=TaskResponse)
async def create_fiction_task(request: FictionRequest):
    """
    创建小说创作任务（异步）

    返回任务ID，可通过任务ID查询进度和结果
    """
    try:
        # 构建上下文
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

        # 创建任务
        task_id = task_manager.create_task(
            task_type=TaskType.FICTION,
            query=request.query,
            context=context
        )

        logger.info(f"创建小说任务: {task_id}")

        return TaskResponse(
            task_id=task_id,
            status="pending",
            message=f"小说创作任务已创建，任务ID: {task_id}"
        )

    except Exception as e:
        logger.error(f"创建小说任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/tasks/ppt", response_model=TaskResponse)
async def create_ppt_task(request: PPTRequest):
    """
    创建PPT生成任务（异步）

    返回任务ID，可通过任务ID查询进度和结果
    """
    try:
        # 构建上下文
        context = {
            'output_type': 'ppt',
            'slides': request.slides,
            'style': request.style,
            'theme': request.theme
        }

        # 创建任务
        task_id = task_manager.create_task(
            task_type=TaskType.PPT,
            query=request.query,
            context=context
        )

        logger.info(f"创建PPT任务: {task_id}")

        return TaskResponse(
            task_id=task_id,
            status="pending",
            message=f"PPT生成任务已创建，任务ID: {task_id}"
        )

    except Exception as e:
        logger.error(f"创建PPT任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    获取任务状态和进度

    返回任务的详细状态信息
    """
    task_info = task_manager.get_task(task_id)

    if not task_info:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

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
    获取任务结果

    只有任务完成后才返回结果
    """
    task_info = task_manager.get_task(task_id)

    if not task_info:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    if task_info.status == TaskStatus.PENDING:
        raise HTTPException(status_code=400, detail="任务还未开始执行")

    if task_info.status == TaskStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail=f"任务正在执行中 ({task_info.progress}%)"
        )

    if task_info.status == TaskStatus.FAILED:
        raise HTTPException(
            status_code=500,
            detail=f"任务执行失败: {task_info.error}"
        )

    if task_info.status == TaskStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="任务已被取消")

    dir = task_info.output_dir
    if not dir:
        dir = f"storage/{task_info.project_id}"

    output_dir = Path(dir)
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="任务输出目录不存在")

    html_path = output_dir / "reports" / "FINAL_REPORT.html"
    if not html_path.exists():
        content = "<p>报告html文件不存在</p>"
    else:
        with html_path.open("r", encoding="utf-8") as f:
            content = f.read()

    md_path = output_dir / "reports" / "FINAL_REPORT.md"
    if not md_path.exists():
        md_content = "报告md文件不存在"
    else:
        with md_path.open("r", encoding="utf-8") as f:
            md_content = f.read()

    # 返回结果
    return {
        "task_id": task_id,
        "status": "completed",
        "result": task_info.result,
        "project_id": task_info.project_id,
        "output_dir": task_info.output_dir,
        "content": content,
        "markdown": md_content
    }


@app.get("/api/v1/tasks/{task_id}/download")
async def download_task_file(
    task_id: str,
    file_type: str = Query("html", description="文件类型: html/md/pdf")
):
    """
    下载任务生成的文件

    支持下载HTML、Markdown等格式
    """
    task_info = task_manager.get_task(task_id)

    if not task_info:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    if task_info.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="任务尚未完成")

    # 构建文件路径
    dir = task_info.output_dir
    if not dir:
        dir = f"storage/{task_info.project_id}"

    output_dir = Path(dir)

    # 根据文件类型查找文件
    if file_type == "html":
        file_path = output_dir / "reports" / "FINAL_REPORT.html"
    elif file_type == "md":
        file_path = output_dir / "reports" / "FINAL_REPORT.md"
    elif file_type == "pdf":
        file_path = output_dir / "exports" / "report.pdf"
    else:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_type}")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"文件不存在: {file_type}")

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=file_path.name
    )


@app.delete("/api/v1/tasks/{task_id}")
async def cancel_task(task_id: str):
    """
    取消任务

    只能取消待执行或正在执行的任务
    """
    success = task_manager.cancel_task(task_id)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="无法取消任务（任务不存在或已完成）"
        )

    return {
        "task_id": task_id,
        "status": "cancelled",
        "message": "任务已取消"
    }


@app.get("/api/v1/tasks")
async def list_tasks(
    status: Optional[str] = Query(None, description="筛选状态"),
    task_type: Optional[str] = Query(None, description="筛选类型"),
    limit: int = Query(50, ge=1, le=200, description="最大数量")
):
    """
    列出任务

    支持按状态和类型筛选
    """
    # 转换筛选参数
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
# 旧版同步搜索端点（保持兼容性）
# ============================================================


@app.get("/search", response_model=SearchResult)
async def search_endpoint(
    q: str = Query(..., description="搜索查询词"),
    k: int = Query(5, ge=1, le=20, description="抓取结果数量"),
    engine: str = Query("duckduckgo", description="搜索引擎"),
    headless: bool = Query(True, description="是否使用无头浏览器")
):
    """
    执行搜索并返回结果

    Args:
        q: 搜索查询词
        k: 抓取结果数量 (1-20)
        engine: 搜索引擎类型
        headless: 是否使用无头浏览器

    Returns:
        搜索结果JSON
    """
    try:
        logger.info(f"API搜索请求: {q} (topk={k}, engine={engine})")

        # 创建临时配置
        temp_config = DeepSearchConfig(
            headless=headless,
            search_engine=engine,
            topk=k
        )

        # 创建临时管道
        temp_pipeline = DeepSearchPipeline(temp_config)

        # 执行搜索
        result = await temp_pipeline.search(q)

        logger.info(f"API搜索完成: {result.success_count}/{result.total_found} 成功")
        return result

    except Exception as e:
        logger.error(f"API搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@app.get("/config")
async def get_config():
    """获取当前配置"""
    return {
        "headless": config.headless,
        "search_engine": config.search_engine,
        "topk": config.topk,
        "shots_dir": config.shots_dir,
        "browser_timeout": config.browser_timeout,
        "page_wait_time": config.page_wait_time
    }


# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"API异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"内部服务器错误: {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)