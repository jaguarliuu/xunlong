"""Langfuse监控集成 - 使用正确的API"""

import os
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from functools import wraps
from loguru import logger
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
    logger.info("Langfuse库已成功导入")
except ImportError as e:
    LANGFUSE_AVAILABLE = False
    logger.warning(f"Langfuse库未安装，监控功能将被禁用: {e}")
    Langfuse = None


class LangfuseMonitor:
    """Langfuse监控器 - 使用正确的API"""
    
    def __init__(self):
        self.enabled = False
        self.langfuse = None
        self.active_traces = {}  # 存储活跃的trace对象
        self.active_generations = {}  # 存储活跃的generation对象
        self.active_spans = {}  # 存储活跃的span对象
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
            logger.info(f"请检查环境变量: LANGFUSE_SECRET_KEY={'已设置' if secret_key else '未设置'}, LANGFUSE_PUB_KEY={'已设置' if public_key else '未设置'}")
            return
        
        try:
            self.langfuse = Langfuse(
                secret_key=secret_key,
                public_key=public_key,
                host=host,
                debug=False
            )
            
            # 测试连接
            self.langfuse.auth_check()
            self.enabled = True
            logger.info(f"Langfuse监控已启用，连接到: {host}")
            
        except Exception as e:
            logger.error(f"Langfuse初始化失败: {e}")
            logger.info("请检查网络连接和API密钥是否正确")
    
    def start_trace(self, name: str, input_data: Dict = None, metadata: Dict = None) -> Optional[str]:
        """开始一个新的trace"""
        if not self.langfuse:
            return None
        
        try:
            # 使用start_observation创建trace根节点
            trace = self.langfuse.start_observation(
                name=name,
                as_type="span",
                input=input_data or {},
                metadata=metadata or {}
            )
            
            trace_id = trace.trace_id
            self.active_traces[trace_id] = trace
            
            logger.info(f"开始trace: {name}, ID: {trace_id}")
            return trace_id
            
        except Exception as e:
            logger.error(f"开始trace失败: {e}")
            return None
    
    def end_trace(self, trace_id: str, output_data: Dict = None, metadata: Dict = None):
        """结束trace"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            # 更新trace的输出和元数据
            if output_data or metadata:
                trace.update(
                    output=output_data,
                    metadata=metadata or {}
                )
            
            # 结束trace
            trace.end()
            del self.active_traces[trace_id]
            
            logger.info(f"结束trace: {trace_id}")
            
        except Exception as e:
            logger.error(f"结束trace失败: {e}")
    
    def log_llm_call(self, trace_id: str, model: str, input_messages: List, 
                     output: str, usage: Dict = None, metadata: Dict = None) -> Optional[str]:
        """记录LLM调用"""
        if not self.langfuse or trace_id not in self.active_traces:
            return None
        
        try:
            trace = self.active_traces[trace_id]
            
            # 使用trace上的start_observation方法创建generation
            generation = trace.start_observation(
                name=f"LLM-{model}",
                as_type="generation",
                model=model,
                input=input_messages,
                output=output,
                usage_details=usage or {},
                metadata=metadata or {}
            )
            
            generation_id = generation.id
            self.active_generations[generation_id] = generation
            
            logger.info(f"记录LLM调用: {model}, generation_id: {generation_id}")
            return generation_id
            
        except Exception as e:
            logger.error(f"记录LLM调用失败: {e}")
            return None
    
    def end_llm_call(self, generation_id: str, output: str = None, usage: Dict = None):
        """结束LLM调用"""
        if not self.langfuse or generation_id not in self.active_generations:
            return
        
        try:
            generation = self.active_generations[generation_id]
            
            # 更新generation
            if output or usage:
                generation.update(
                    output=output,
                    usage_details=usage or {}
                )
            
            generation.end()
            del self.active_generations[generation_id]
            
            logger.info(f"结束LLM调用: {generation_id}")
            
        except Exception as e:
            logger.error(f"结束LLM调用失败: {e}")
    
    def log_agent_action(self, trace_id: str, agent_name: str, action: str, 
                        input_data: Any = None, output_data: Any = None,
                        metadata: Dict = None) -> Optional[str]:
        """记录Agent动作"""
        if not self.langfuse or trace_id not in self.active_traces:
            return None
        
        try:
            trace = self.active_traces[trace_id]
            
            # 使用trace上的start_span方法
            span = trace.start_span(
                name=f"Agent-{agent_name}-{action}",
                input=input_data,
                output=output_data,
                metadata=metadata or {}
            )
            
            span_id = span.id
            self.active_spans[span_id] = span
            
            logger.info(f"记录Agent动作: {agent_name}-{action}, span_id: {span_id}")
            return span_id
            
        except Exception as e:
            logger.error(f"记录Agent动作失败: {e}")
            return None
    
    def end_agent_action(self, span_id: str, output_data: Any = None, metadata: Dict = None):
        """结束Agent动作"""
        if not self.langfuse or span_id not in self.active_spans:
            return
        
        try:
            span = self.active_spans[span_id]
            
            # 更新span
            if output_data or metadata:
                span.update(
                    output=output_data,
                    metadata=metadata or {}
                )
            
            span.end()
            del self.active_spans[span_id]
            
            logger.info(f"结束Agent动作: {span_id}")
            
        except Exception as e:
            logger.error(f"结束Agent动作失败: {e}")
    
    def log_search_action(self, trace_id: str, query: str, results_count: int,
                         search_time: float, metadata: Dict = None):
        """记录搜索动作"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            span = trace.start_span(
                name="Web-Search",
                input={"query": query},
                output={"results_count": results_count, "search_time": search_time},
                metadata=metadata or {}
            )
            
            # 立即结束搜索span
            span.end()
            
            logger.info(f"记录搜索动作: {query} -> {results_count}个结果")
            
        except Exception as e:
            logger.error(f"记录搜索动作失败: {e}")
    
    def log_content_extraction(self, trace_id: str, url: str, content_length: int,
                              extraction_time: float, success: bool,
                              metadata: Dict = None):
        """记录内容提取"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            span = trace.start_span(
                name="Content-Extraction",
                input={"url": url},
                output={
                    "content_length": content_length,
                    "extraction_time": extraction_time,
                    "success": success
                },
                metadata=metadata or {}
            )
            
            # 立即结束提取span
            span.end()
            
            logger.info(f"记录内容提取: {url} -> {content_length}字符")
            
        except Exception as e:
            logger.error(f"记录内容提取失败: {e}")
    
    def log_evaluation(self, trace_id: str, content_items: int, 
                      relevant_items: int, evaluation_time: float,
                      metadata: Dict = None):
        """记录内容评估"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            span = trace.start_span(
                name="Content-Evaluation",
                input={"content_items": content_items},
                output={
                    "relevant_items": relevant_items,
                    "relevance_rate": relevant_items / content_items if content_items > 0 else 0,
                    "evaluation_time": evaluation_time
                },
                metadata=metadata or {}
            )
            
            # 立即结束评估span
            span.end()
            
            logger.info(f"记录内容评估: {relevant_items}/{content_items}相关")
            
        except Exception as e:
            logger.error(f"记录内容评估失败: {e}")
    
    def log_report_generation(self, trace_id: str, report_type: str, 
                             word_count: int, generation_time: float,
                             metadata: Dict = None):
        """记录报告生成"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            span = trace.start_span(
                name="Report-Generation",
                input={"report_type": report_type},
                output={
                    "word_count": word_count,
                    "generation_time": generation_time
                },
                metadata=metadata or {}
            )
            
            # 立即结束报告生成span
            span.end()
            
            logger.info(f"记录报告生成: {report_type} -> {word_count}字")
            
        except Exception as e:
            logger.error(f"记录报告生成失败: {e}")
    
    def log_event(self, trace_id: str, name: str, input_data: Any = None, 
                  metadata: Dict = None):
        """记录事件"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            event = trace.create_event(
                name=name,
                input=input_data,
                metadata=metadata or {}
            )
            
            logger.info(f"记录事件: {name}")
            return event.id
            
        except Exception as e:
            logger.error(f"记录事件失败: {e}")
            return None
    
    def flush(self):
        """刷新缓冲区，确保所有数据都被发送"""
        if self.enabled and self.langfuse:
            try:
                self.langfuse.flush()
                logger.info("Langfuse数据已刷新")
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
            span_id = None
            
            try:
                # 开始记录Agent动作
                span_id = monitor.log_agent_action(
                    trace_id=trace_id,
                    agent_name=agent_name,
                    action=action,
                    input_data={"args": str(args[1:])[:500], "kwargs": str(kwargs)[:500]},
                    metadata={"start_time": start_time}
                )
                
                result = await func(*args, **kwargs)
                
                # 结束记录Agent动作
                if span_id:
                    monitor.end_agent_action(
                        span_id=span_id,
                        output_data=str(result)[:1000] if result else None,
                        metadata={"execution_time": time.time() - start_time, "success": True}
                    )
                
                return result
                
            except Exception as e:
                # 记录错误
                if span_id:
                    monitor.end_agent_action(
                        span_id=span_id,
                        output_data=None,
                        metadata={
                            "execution_time": time.time() - start_time,
                            "success": False,
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
            span_id = None
            
            try:
                # 开始记录Agent动作
                span_id = monitor.log_agent_action(
                    trace_id=trace_id,
                    agent_name=agent_name,
                    action=action,
                    input_data={"args": str(args[1:])[:500], "kwargs": str(kwargs)[:500]},
                    metadata={"start_time": start_time}
                )
                
                result = func(*args, **kwargs)
                
                # 结束记录Agent动作
                if span_id:
                    monitor.end_agent_action(
                        span_id=span_id,
                        output_data=str(result)[:1000] if result else None,
                        metadata={"execution_time": time.time() - start_time, "success": True}
                    )
                
                return result
                
            except Exception as e:
                # 记录错误
                if span_id:
                    monitor.end_agent_action(
                        span_id=span_id,
                        output_data=None,
                        metadata={
                            "execution_time": time.time() - start_time,
                            "success": False,
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