"""Langfuse监控集成"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from functools import wraps
from loguru import logger

try:
    from langfuse import Langfuse
    from langfuse.decorators import observe, langfuse_context
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logger.warning("Langfuse库未安装，监控功能将被禁用")


class LangfuseMonitor:
    """Langfuse监控器"""
    
    def __init__(self):
        self.enabled = False
        self.langfuse = None
        self.active_traces = {}  # 存储活跃的追踪
        self._initialize()
    
    def _initialize(self):
        """初始化Langfuse客户端"""
        if not LANGFUSE_AVAILABLE:
            logger.warning("Langfuse不可用，监控功能已禁用")
            return
        
        # 从环境变量获取配置
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        public_key = os.getenv("LANGFUSE_PUB_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if not secret_key or not public_key:
            logger.warning("Langfuse配置不完整，监控功能已禁用")
            return
        
        try:
            self.langfuse = Langfuse(
                secret_key=secret_key,
                public_key=public_key,
                host=host
            )
            self.enabled = True
            logger.info("Langfuse监控已启用")
        except Exception as e:
            logger.error(f"Langfuse初始化失败: {e}")
    
    def start_trace(self, trace_id: str, name: str, input_data: Any = None, 
                   metadata: Optional[Dict] = None):
        """开始追踪"""
        if not self.enabled:
            return
        
        try:
            trace = self.langfuse.trace(
                id=trace_id,
                name=name,
                input=input_data,
                metadata=metadata or {}
            )
            self.active_traces[trace_id] = trace
            logger.debug(f"开始追踪: {trace_id} - {name}")
        except Exception as e:
            logger.error(f"开始追踪失败: {e}")
    
    def end_trace(self, trace_id: str, output_data: Any = None, 
                 metadata: Optional[Dict] = None):
        """结束追踪"""
        if not self.enabled:
            return
        
        try:
            if trace_id in self.active_traces:
                trace = self.active_traces[trace_id]
                trace.update(
                    output=output_data,
                    metadata=metadata or {}
                )
                del self.active_traces[trace_id]
                logger.debug(f"结束追踪: {trace_id}")
        except Exception as e:
            logger.error(f"结束追踪失败: {e}")
    
    def create_trace(self, name: str, user_id: Optional[str] = None, 
                    session_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """创建追踪"""
        if not self.enabled:
            return None
        
        try:
            return self.langfuse.trace(
                name=name,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"创建追踪失败: {e}")
            return None
    
    def create_span(self, trace_id: str, name: str, input_data: Any = None, 
                   metadata: Optional[Dict] = None):
        """创建跨度"""
        if not self.enabled:
            return None
        
        try:
            return self.langfuse.span(
                trace_id=trace_id,
                name=name,
                input=input_data,
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"创建跨度失败: {e}")
            return None
    
    def log_llm_call(self, trace_id: str, model: str, input_messages: List[Dict], 
                    output: str, usage: Optional[Dict] = None, 
                    metadata: Optional[Dict] = None):
        """记录LLM调用"""
        if not self.enabled:
            return
        
        try:
            self.langfuse.generation(
                trace_id=trace_id,
                name=f"LLM-{model}",
                model=model,
                input=input_messages,
                output=output,
                usage=usage,
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"记录LLM调用失败: {e}")
    
    def log_agent_action(self, trace_id: str, agent_name: str, action: str, 
                        input_data: Any = None, output_data: Any = None,
                        metadata: Optional[Dict] = None):
        """记录Agent动作"""
        if not self.enabled:
            return
        
        try:
            self.langfuse.span(
                trace_id=trace_id,
                name=f"Agent-{agent_name}-{action}",
                input=input_data,
                output=output_data,
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"记录Agent动作失败: {e}")
    
    def log_search_action(self, trace_id: str, query: str, results_count: int,
                         search_time: float, metadata: Optional[Dict] = None):
        """记录搜索动作"""
        if not self.enabled:
            return
        
        try:
            self.langfuse.span(
                trace_id=trace_id,
                name="Web-Search",
                input={"query": query},
                output={"results_count": results_count, "search_time": search_time},
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"记录搜索动作失败: {e}")
    
    def log_content_extraction(self, trace_id: str, url: str, content_length: int,
                              extraction_time: float, success: bool,
                              metadata: Optional[Dict] = None):
        """记录内容提取"""
        if not self.enabled:
            return
        
        try:
            self.langfuse.span(
                trace_id=trace_id,
                name="Content-Extraction",
                input={"url": url},
                output={
                    "content_length": content_length,
                    "extraction_time": extraction_time,
                    "success": success
                },
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"记录内容提取失败: {e}")
    
    def log_evaluation(self, trace_id: str, content_items: int, 
                      relevant_items: int, evaluation_time: float,
                      metadata: Optional[Dict] = None):
        """记录内容评估"""
        if not self.enabled:
            return
        
        try:
            self.langfuse.span(
                trace_id=trace_id,
                name="Content-Evaluation",
                input={"content_items": content_items},
                output={
                    "relevant_items": relevant_items,
                    "relevance_rate": relevant_items / content_items if content_items > 0 else 0,
                    "evaluation_time": evaluation_time
                },
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"记录内容评估失败: {e}")
    
    def log_report_generation(self, trace_id: str, report_type: str, 
                             word_count: int, generation_time: float,
                             metadata: Optional[Dict] = None):
        """记录报告生成"""
        if not self.enabled:
            return
        
        try:
            self.langfuse.span(
                trace_id=trace_id,
                name="Report-Generation",
                input={"report_type": report_type},
                output={
                    "word_count": word_count,
                    "generation_time": generation_time
                },
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"记录报告生成失败: {e}")
    
    def flush(self):
        """刷新缓冲区，确保所有数据都被发送"""
        if self.enabled and self.langfuse:
            try:
                self.langfuse.flush()
            except Exception as e:
                logger.error(f"刷新Langfuse缓冲区失败: {e}")


# 全局监控实例
monitor = LangfuseMonitor()


def trace_agent_method(agent_name: str, action: str):
    """装饰器：追踪Agent方法"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not monitor.enabled:
                return await func(*args, **kwargs)
            
            trace_id = getattr(args[0], '_trace_id', None)
            if not trace_id:
                return await func(*args, **kwargs)
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                monitor.log_agent_action(
                    trace_id=trace_id,
                    agent_name=agent_name,
                    action=action,
                    input_data={"args": str(args[1:]), "kwargs": str(kwargs)},
                    output_data=str(result)[:1000] if result else None,
                    metadata={"execution_time": time.time() - start_time}
                )
                return result
            except Exception as e:
                monitor.log_agent_action(
                    trace_id=trace_id,
                    agent_name=agent_name,
                    action=action,
                    input_data={"args": str(args[1:]), "kwargs": str(kwargs)},
                    output_data=None,
                    metadata={
                        "execution_time": time.time() - start_time,
                        "error": str(e)
                    }
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not monitor.enabled:
                return func(*args, **kwargs)
            
            trace_id = getattr(args[0], '_trace_id', None)
            if not trace_id:
                return func(*args, **kwargs)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                monitor.log_agent_action(
                    trace_id=trace_id,
                    agent_name=agent_name,
                    action=action,
                    input_data={"args": str(args[1:]), "kwargs": str(kwargs)},
                    output_data=str(result)[:1000] if result else None,
                    metadata={"execution_time": time.time() - start_time}
                )
                return result
            except Exception as e:
                monitor.log_agent_action(
                    trace_id=trace_id,
                    agent_name=agent_name,
                    action=action,
                    input_data={"args": str(args[1:]), "kwargs": str(kwargs)},
                    output_data=None,
                    metadata={
                        "execution_time": time.time() - start_time,
                        "error": str(e)
                    }
                )
                raise
        
        # 根据函数是否为协程选择包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator