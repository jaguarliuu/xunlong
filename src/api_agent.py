"""DeepSearch智能体系统API接口"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("警告: FastAPI库未安装，无法启动API服务")

from .deep_search_agent import DeepSearchAgent

if not FASTAPI_AVAILABLE:
    raise ImportError("请安装FastAPI: pip install fastapi uvicorn")

# 创建FastAPI应用
app = FastAPI(
    title="DeepSearch智能体系统API",
    description="基于LangGraph的多agent协作深度搜索API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局智能体实例
agent: Optional[DeepSearchAgent] = None


# 请求模型
class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str = Field(..., description="搜索查询", min_length=1)
    context: Optional[Dict[str, Any]] = Field(None, description="搜索上下文")
    config: Optional[Dict[str, Any]] = Field(None, description="搜索配置")


class QuickAnswerRequest(BaseModel):
    """快速回答请求模型"""
    query: str = Field(..., description="查询问题", min_length=1)


class SearchConfig(BaseModel):
    """搜索配置模型"""
    max_search_results: Optional[int] = Field(5, description="最大搜索结果数", ge=1, le=20)
    synthesis_config: Optional[Dict[str, Any]] = Field(None, description="综合配置")
    timeout_seconds: Optional[int] = Field(300, description="超时时间(秒)", ge=30, le=600)


# 响应模型
class SearchResponse(BaseModel):
    """搜索响应模型"""
    status: str = Field(..., description="搜索状态")
    user_query: str = Field(..., description="用户查询")
    optimization_result: Optional[Dict[str, Any]] = Field(None, description="查询优化结果")
    search_results: Optional[Dict[str, Any]] = Field(None, description="搜索结果")
    analysis_results: Optional[List[Dict[str, Any]]] = Field(None, description="分析结果")
    final_report: Optional[Dict[str, Any]] = Field(None, description="最终报告")
    execution_steps: Optional[List[str]] = Field(None, description="执行步骤")
    errors: Optional[List[str]] = Field(None, description="错误信息")
    timestamp: str = Field(..., description="响应时间戳")


class QuickAnswerResponse(BaseModel):
    """快速回答响应模型"""
    query: str = Field(..., description="查询问题")
    answer: str = Field(..., description="回答内容")
    timestamp: str = Field(..., description="响应时间戳")


class SystemStatusResponse(BaseModel):
    """系统状态响应模型"""
    llm_manager: Dict[str, Any] = Field(..., description="LLM管理器状态")
    agents_status: Dict[str, Any] = Field(..., description="智能体状态")
    coordinator_config: Dict[str, Any] = Field(..., description="协调器配置")
    timestamp: str = Field(..., description="状态时间戳")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细信息")
    timestamp: str = Field(..., description="错误时间戳")


# 启动事件
@app.on_event("startup")
async def startup_event():
    """启动时初始化智能体"""
    global agent
    try:
        agent = DeepSearchAgent()
        print("✓ DeepSearch智能体系统API启动成功")
    except Exception as e:
        print(f"✗ 智能体初始化失败: {e}")
        raise


# API端点
@app.get("/", summary="API根路径")
async def root():
    """API根路径"""
    return {
        "message": "DeepSearch智能体系统API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.post("/search", response_model=SearchResponse, summary="执行深度搜索")
async def search_endpoint(request: SearchRequest):
    """执行深度搜索"""
    if not agent:
        raise HTTPException(status_code=500, detail="智能体未初始化")
    
    try:
        result = await agent.search(
            query=request.query,
            context=request.context,
            config=request.config
        )
        
        return SearchResponse(
            **result,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"搜索执行失败: {str(e)}"
        )


@app.post("/quick", response_model=QuickAnswerResponse, summary="快速回答")
async def quick_answer_endpoint(request: QuickAnswerRequest):
    """快速回答"""
    if not agent:
        raise HTTPException(status_code=500, detail="智能体未初始化")
    
    try:
        answer = await agent.quick_answer(request.query)
        
        return QuickAnswerResponse(
            query=request.query,
            answer=answer,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"快速回答失败: {str(e)}"
        )


@app.get("/status", response_model=SystemStatusResponse, summary="获取系统状态")
async def status_endpoint():
    """获取系统状态"""
    if not agent:
        raise HTTPException(status_code=500, detail="智能体未初始化")
    
    try:
        status = agent.get_system_status()
        
        return SystemStatusResponse(
            **status,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取状态失败: {str(e)}"
        )


@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查"""
    if not agent:
        return {"status": "unhealthy", "message": "智能体未初始化"}
    
    try:
        # 简单的健康检查
        status = agent.get_system_status()
        return {
            "status": "healthy",
            "agents_count": len(status["agents_status"]),
            "llm_configs": status["llm_manager"]["total_configs"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/test", summary="测试系统连接")
async def test_connections():
    """测试系统连接"""
    if not agent:
        raise HTTPException(status_code=500, detail="智能体未初始化")
    
    try:
        results = agent.test_connections()
        
        return {
            "test_results": results,
            "total_configs": len(results),
            "successful_configs": sum(1 for success in results.values() if success),
            "failed_configs": sum(1 for success in results.values() if not success),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"连接测试失败: {str(e)}"
        )


@app.post("/reload", summary="重新加载提示词")
async def reload_prompts():
    """重新加载提示词"""
    if not agent:
        raise HTTPException(status_code=500, detail="智能体未初始化")
    
    try:
        agent.reload_prompts()
        
        return {
            "message": "提示词重新加载成功",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"重新加载提示词失败: {str(e)}"
        )


@app.post("/reset", summary="重置智能体状态")
async def reset_agents():
    """重置智能体状态"""
    if not agent:
        raise HTTPException(status_code=500, detail="智能体未初始化")
    
    try:
        agent.reset_agents()
        
        return {
            "message": "智能体状态重置成功",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"重置智能体失败: {str(e)}"
        )


# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return ErrorResponse(
        error="内部服务器错误",
        detail=str(exc),
        timestamp=datetime.now().isoformat()
    )


def run_api(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info"
):
    """运行API服务"""
    uvicorn.run(
        "src.api_agent:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )


if __name__ == "__main__":
    run_api()