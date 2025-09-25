"""REST API接口模块"""

import json
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from loguru import logger

from .config import DeepSearchConfig
from .pipeline import DeepSearchPipeline
from .models import SearchResult


# 创建FastAPI应用
app = FastAPI(
    title="DeepSearch API",
    description="智能搜索与内容抽取API",
    version="0.1.0"
)

# 全局配置和管道
config = DeepSearchConfig()
pipeline = DeepSearchPipeline(config)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "DeepSearch API",
        "version": "0.1.0",
        "description": "智能搜索与内容抽取API"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


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