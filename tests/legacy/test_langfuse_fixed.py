#!/usr/bin/env python3
"""Langfuse API"""

import os
import time
from dotenv import load_dotenv
load_dotenv()

try:
    from langfuse import Langfuse
    
    # 
    langfuse = Langfuse(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUB_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    
    print(" Langfuse")
    
    # 
    langfuse.auth_check()
    print(" ")
    
    # trace ID
    trace_id = f"test-trace-{int(time.time())}"
    print(f"trace ID: {trace_id}")
    
    # trace
    event = langfuse.create_event(
        trace_id=trace_id,
        name="trace-start-test",
        input={"test": "data"},
        metadata={"version": "1.0.0"}
    )
    print(f" : {event.id}")
    
    # generation (LLM)
    generation = langfuse.start_generation(
        trace_id=trace_id,
        name="LLM-test-model",
        model="test-model",
        input=[{"role": "user", "content": "Hello"}],
        output="Hi there!",
        usage={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
        metadata={"test": True}
    )
    print(f" generation: {generation.id}")
    
    # span (Agent)
    span = langfuse.start_span(
        trace_id=trace_id,
        name="Agent-TestAgent-test_action",
        input={"action": "test"},
        output={"result": "success"},
        metadata={"duration": 1.5}
    )
    print(f" span: {span.id}")
    
    # 
    langfuse.flush()
    print(" Langfuse")
    print(f" {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')} ")
    
except ImportError as e:
    print(f" Langfuse: {e}")
except Exception as e:
    print(f" : {e}")
    import traceback
    traceback.print_exc()