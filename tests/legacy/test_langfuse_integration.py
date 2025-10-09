#!/usr/bin/env python3
"""Langfuse"""

import os
import sys
import time
from pathlib import Path

# Python
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 
from dotenv import load_dotenv
load_dotenv()

from src.monitoring.langfuse_monitor import monitor
from loguru import logger

def test_langfuse_connection():
    """Langfuse"""
    logger.info("=== Langfuse ===")
    
    # 
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    public_key = os.getenv("LANGFUSE_PUB_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    logger.info(f"LANGFUSE_SECRET_KEY: {'' if secret_key else ''}")
    logger.info(f"LANGFUSE_PUB_KEY: {'' if public_key else ''}")
    logger.info(f"LANGFUSE_HOST: {host}")
    
    # 
    logger.info(f": {monitor.enabled}")
    
    if not monitor.enabled:
        logger.error("Langfuse")
        return False
    
    # 
    try:
        trace_id = f"test-trace-{int(time.time())}"
        logger.info(f": {trace_id}")
        
        # 
        monitor.start_trace(
            trace_id=trace_id,
            name="Langfuse",
            input_data={"test": "integration"},
            metadata={"version": "1.0.0", "environment": "test"}
        )
        
        # LLM
        monitor.log_llm_call(
            trace_id=trace_id,
            model="test-model",
            input_messages=[{"role": "user", "content": ""}],
            output="",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            metadata={"test": True}
        )
        
        # Agent
        monitor.log_agent_action(
            trace_id=trace_id,
            agent_name="TestAgent",
            action="test_action",
            input_data={"input": "test"},
            output_data={"output": "success"},
            metadata={"duration": 1.5}
        )
        
        # 
        monitor.end_trace(
            trace_id=trace_id,
            output_data={"result": "success"},
            metadata={"total_duration": 2.0}
        )
        
        # 
        monitor.flush()
        
        logger.success(" Langfuse")
        logger.info(f" {host} ")
        return True
        
    except Exception as e:
        logger.error(f" Langfuse: {e}")
        return False

if __name__ == "__main__":
    success = test_langfuse_connection()
    sys.exit(0 if success else 1)