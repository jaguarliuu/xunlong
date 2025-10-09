"""DeepSearchAPI"""

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
    print(": FastAPIAPI")

from .deep_search_agent import DeepSearchAgent

if not FASTAPI_AVAILABLE:
    raise ImportError("FastAPI: pip install fastapi uvicorn")

# FastAPI
app = FastAPI(
    title="DeepSearchAPI",
    description="LangGraphagentAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
agent: Optional[DeepSearchAgent] = None


# 
class SearchRequest(BaseModel):
    """TODO: Add docstring."""
    query: str = Field(..., description="", min_length=1)
    context: Optional[Dict[str, Any]] = Field(None, description="")
    config: Optional[Dict[str, Any]] = Field(None, description="")


class QuickAnswerRequest(BaseModel):
    """TODO: Add docstring."""
    query: str = Field(..., description="", min_length=1)


class SearchConfig(BaseModel):
    """TODO: Add docstring."""
    max_search_results: Optional[int] = Field(5, description="", ge=1, le=20)
    synthesis_config: Optional[Dict[str, Any]] = Field(None, description="")
    timeout_seconds: Optional[int] = Field(300, description="()", ge=30, le=600)


# 
class SearchResponse(BaseModel):
    """TODO: Add docstring."""
    status: str = Field(..., description="")
    user_query: str = Field(..., description="")
    optimization_result: Optional[Dict[str, Any]] = Field(None, description="")
    search_results: Optional[Dict[str, Any]] = Field(None, description="")
    analysis_results: Optional[List[Dict[str, Any]]] = Field(None, description="")
    final_report: Optional[Dict[str, Any]] = Field(None, description="")
    execution_steps: Optional[List[str]] = Field(None, description="")
    errors: Optional[List[str]] = Field(None, description="")
    timestamp: str = Field(..., description="")


class QuickAnswerResponse(BaseModel):
    """TODO: Add docstring."""
    query: str = Field(..., description="")
    answer: str = Field(..., description="")
    timestamp: str = Field(..., description="")


class SystemStatusResponse(BaseModel):
    """TODO: Add docstring."""
    llm_manager: Dict[str, Any] = Field(..., description="LLM")
    agents_status: Dict[str, Any] = Field(..., description="")
    coordinator_config: Dict[str, Any] = Field(..., description="")
    timestamp: str = Field(..., description="")


class ErrorResponse(BaseModel):
    """TODO: Add docstring."""
    error: str = Field(..., description="")
    detail: Optional[str] = Field(None, description="")
    timestamp: str = Field(..., description="")


# 
@app.on_event("startup")
async def startup_event():
    """TODO: Add docstring."""
    global agent
    try:
        agent = DeepSearchAgent()
        print(" DeepSearchAPI")
    except Exception as e:
        print(f" : {e}")
        raise


# API
@app.get("/", summary="API")
async def root():
    """API"""
    return {
        "message": "DeepSearchAPI",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.post("/search", response_model=SearchResponse, summary="")
async def search_endpoint(request: SearchRequest):
    """TODO: Add docstring."""
    if not agent:
        raise HTTPException(status_code=500, detail="")
    
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
            detail=f": {str(e)}"
        )


@app.post("/quick", response_model=QuickAnswerResponse, summary="")
async def quick_answer_endpoint(request: QuickAnswerRequest):
    """TODO: Add docstring."""
    if not agent:
        raise HTTPException(status_code=500, detail="")
    
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
            detail=f": {str(e)}"
        )


@app.get("/status", response_model=SystemStatusResponse, summary="")
async def status_endpoint():
    """TODO: Add docstring."""
    if not agent:
        raise HTTPException(status_code=500, detail="")
    
    try:
        status = agent.get_system_status()
        
        return SystemStatusResponse(
            **status,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f": {str(e)}"
        )


@app.get("/health", summary="")
async def health_check():
    """TODO: Add docstring."""
    if not agent:
        return {"status": "unhealthy", "message": ""}
    
    try:
        # 
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


@app.post("/test", summary="")
async def test_connections():
    """TODO: Add docstring."""
    if not agent:
        raise HTTPException(status_code=500, detail="")
    
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
            detail=f": {str(e)}"
        )


@app.post("/reload", summary="")
async def reload_prompts():
    """TODO: Add docstring."""
    if not agent:
        raise HTTPException(status_code=500, detail="")
    
    try:
        agent.reload_prompts()
        
        return {
            "message": "",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f": {str(e)}"
        )


@app.post("/reset", summary="")
async def reset_agents():
    """TODO: Add docstring."""
    if not agent:
        raise HTTPException(status_code=500, detail="")
    
    try:
        agent.reset_agents()
        
        return {
            "message": "",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f": {str(e)}"
        )


# 
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """TODO: Add docstring."""
    return ErrorResponse(
        error="",
        detail=str(exc),
        timestamp=datetime.now().isoformat()
    )


def run_api(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info"
):
    """API"""
    uvicorn.run(
        "src.api_agent:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )


if __name__ == "__main__":
    run_api()