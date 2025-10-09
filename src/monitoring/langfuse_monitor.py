"""Langfuse - API"""

import os
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from functools import wraps
from loguru import logger

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
    logger.info("Langfuse")
except ImportError as e:
    LANGFUSE_AVAILABLE = False
    logger.warning(f"Langfuse: {e}")
    Langfuse = None


class LangfuseMonitor:
    """Langfuse - API"""
    
    def __init__(self):
        self.enabled = False
        self.langfuse = None
        self.active_traces = {}  # trace
        self.active_generations = {}  # generation
        self.active_spans = {}  # span
        self._initialize()
    
    def _initialize(self):
        """Langfuse"""
        if not LANGFUSE_AVAILABLE:
            logger.warning("Langfuse")
            return
        
        # 
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        public_key = os.getenv("LANGFUSE_PUB_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if not secret_key or not public_key:
            logger.warning("Langfuse")
            logger.info(f": LANGFUSE_SECRET_KEY={'' if secret_key else ''}, LANGFUSE_PUB_KEY={'' if public_key else ''}")
            return
        
        try:
            self.langfuse = Langfuse(
                secret_key=secret_key,
                public_key=public_key,
                host=host,
                debug=False
            )
            
            # 
            self.langfuse.auth_check()
            self.enabled = True
            logger.info(f"Langfuse: {host}")
            
        except Exception as e:
            logger.error(f"Langfuse: {e}")
            logger.info("API")
    
    def start_trace(self, name: str, input_data: Dict = None, metadata: Dict = None) -> Optional[str]:
        """trace"""
        if not self.langfuse:
            return None
        
        try:
            # start_observationtrace
            trace = self.langfuse.start_observation(
                name=name,
                as_type="span",
                input=input_data or {},
                metadata=metadata or {}
            )
            
            trace_id = trace.trace_id
            self.active_traces[trace_id] = trace
            
            logger.info(f"trace: {name}, ID: {trace_id}")
            return trace_id
            
        except Exception as e:
            logger.error(f"trace: {e}")
            return None
    
    def end_trace(self, trace_id: str, output_data: Dict = None, metadata: Dict = None):
        """trace"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            # trace
            if output_data or metadata:
                trace.update(
                    output=output_data,
                    metadata=metadata or {}
                )
            
            # trace
            trace.end()
            del self.active_traces[trace_id]
            
            logger.info(f"trace: {trace_id}")
            
        except Exception as e:
            logger.error(f"trace: {e}")
    
    def log_llm_call(self, trace_id: str, model: str, input_messages: List, 
                     output: str, usage: Dict = None, metadata: Dict = None) -> Optional[str]:
        """LLM"""
        if not self.langfuse or trace_id not in self.active_traces:
            return None
        
        try:
            trace = self.active_traces[trace_id]
            
            # tracestart_observationgeneration
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
            
            logger.info(f"LLM: {model}, generation_id: {generation_id}")
            return generation_id
            
        except Exception as e:
            logger.error(f"LLM: {e}")
            return None
    
    def end_llm_call(self, generation_id: str, output: str = None, usage: Dict = None):
        """LLM"""
        if not self.langfuse or generation_id not in self.active_generations:
            return
        
        try:
            generation = self.active_generations[generation_id]
            
            # generation
            if output or usage:
                generation.update(
                    output=output,
                    usage_details=usage or {}
                )
            
            generation.end()
            del self.active_generations[generation_id]
            
            logger.info(f"LLM: {generation_id}")
            
        except Exception as e:
            logger.error(f"LLM: {e}")
    
    def log_agent_action(self, trace_id: str, agent_name: str, action: str, 
                        input_data: Any = None, output_data: Any = None,
                        metadata: Dict = None) -> Optional[str]:
        """Agent"""
        if not self.langfuse or trace_id not in self.active_traces:
            return None
        
        try:
            trace = self.active_traces[trace_id]
            
            # tracestart_span
            span = trace.start_span(
                name=f"Agent-{agent_name}-{action}",
                input=input_data,
                output=output_data,
                metadata=metadata or {}
            )
            
            span_id = span.id
            self.active_spans[span_id] = span
            
            logger.info(f"Agent: {agent_name}-{action}, span_id: {span_id}")
            return span_id
            
        except Exception as e:
            logger.error(f"Agent: {e}")
            return None
    
    def end_agent_action(self, span_id: str, output_data: Any = None, metadata: Dict = None):
        """Agent"""
        if not self.langfuse or span_id not in self.active_spans:
            return
        
        try:
            span = self.active_spans[span_id]
            
            # span
            if output_data or metadata:
                span.update(
                    output=output_data,
                    metadata=metadata or {}
                )
            
            span.end()
            del self.active_spans[span_id]
            
            logger.info(f"Agent: {span_id}")
            
        except Exception as e:
            logger.error(f"Agent: {e}")
    
    def log_search_action(self, trace_id: str, query: str, results_count: int,
                         search_time: float, metadata: Dict = None):
        """TODO: Add docstring."""
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
            
            # span
            span.end()
            
            logger.info(f": {query} -> {results_count}")
            
        except Exception as e:
            logger.error(f": {e}")
    
    def log_content_extraction(self, trace_id: str, url: str, content_length: int,
                              extraction_time: float, success: bool,
                              metadata: Dict = None):
        """TODO: Add docstring."""
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
            
            # span
            span.end()
            
            logger.info(f": {url} -> {content_length}")
            
        except Exception as e:
            logger.error(f": {e}")
    
    def log_evaluation(self, trace_id: str, content_items: int, 
                      relevant_items: int, evaluation_time: float,
                      metadata: Dict = None):
        """TODO: Add docstring."""
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
            
            # span
            span.end()
            
            logger.info(f": {relevant_items}/{content_items}")
            
        except Exception as e:
            logger.error(f": {e}")
    
    def log_report_generation(self, trace_id: str, report_type: str, 
                             word_count: int, generation_time: float,
                             metadata: Dict = None):
        """TODO: Add docstring."""
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
            
            # span
            span.end()
            
            logger.info(f": {report_type} -> {word_count}")
            
        except Exception as e:
            logger.error(f": {e}")
    
    def log_event(self, trace_id: str, name: str, input_data: Any = None, 
                  metadata: Dict = None):
        """TODO: Add docstring."""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            event = trace.create_event(
                name=name,
                input=input_data,
                metadata=metadata or {}
            )
            
            logger.info(f": {name}")
            return event.id
            
        except Exception as e:
            logger.error(f": {e}")
            return None
    
    def flush(self):
        """TODO: Add docstring."""
        if self.enabled and self.langfuse:
            try:
                self.langfuse.flush()
                logger.info("Langfuse")
            except Exception as e:
                logger.error(f"Langfuse: {e}")


# 
monitor = LangfuseMonitor()


def trace_agent_method(agent_name: str, action: str):
    """Agent"""
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
                # Agent
                span_id = monitor.log_agent_action(
                    trace_id=trace_id,
                    agent_name=agent_name,
                    action=action,
                    input_data={"args": str(args[1:])[:500], "kwargs": str(kwargs)[:500]},
                    metadata={"start_time": start_time}
                )
                
                result = await func(*args, **kwargs)
                
                # Agent
                if span_id:
                    monitor.end_agent_action(
                        span_id=span_id,
                        output_data=str(result)[:1000] if result else None,
                        metadata={"execution_time": time.time() - start_time, "success": True}
                    )
                
                return result
                
            except Exception as e:
                # 
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
                # Agent
                span_id = monitor.log_agent_action(
                    trace_id=trace_id,
                    agent_name=agent_name,
                    action=action,
                    input_data={"args": str(args[1:])[:500], "kwargs": str(kwargs)[:500]},
                    metadata={"start_time": start_time}
                )
                
                result = func(*args, **kwargs)
                
                # Agent
                if span_id:
                    monitor.end_agent_action(
                        span_id=span_id,
                        output_data=str(result)[:1000] if result else None,
                        metadata={"execution_time": time.time() - start_time, "success": True}
                    )
                
                return result
                
            except Exception as e:
                # 
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
        
        # 
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator