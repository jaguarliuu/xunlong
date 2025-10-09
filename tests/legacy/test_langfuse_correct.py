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
    
    # trace (start_observationtrace)
    trace = langfuse.start_observation(
        name="DeepSearch-Test-Trace",
        as_type="span",
        input={"query": ""},
        metadata={"version": "1.0.0", "test": True}
    )
    print(f" trace: {trace.id}")
    
    # generation (LLM) - trace
    generation = langfuse.start_generation(
        trace_context=trace.get_trace_context(),
        name="LLM-Qianwen-Call",
        model="qwen-turbo",
        input=[{"role": "user", "content": "Hello"}],
        output="Hi there!",
        usage_details={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
        metadata={"temperature": 0.7}
    )
    print(f" generation: {generation.id}")
    
    # span (Agent) - trace
    span = langfuse.start_span(
        trace_context=trace.get_trace_context(),
        name="Agent-DeepSearcher-search",
        input={"query": "", "max_results": 10},
        output={"results_count": 5, "status": "success"},
        metadata={"duration": 2.5, "search_engine": "duckduckgo"}
    )
    print(f" span: {span.id}")
    
    #  - trace
    event = langfuse.create_event(
        trace_context=trace.get_trace_context(),
        name="search-completed",
        input={"query": ""},
        metadata={"timestamp": time.time()}
    )
    print(f" event: {event.id}")
    
    # 
    generation.end()
    span.end()
    trace.end()
    
    # 
    langfuse.flush()
    print(" Langfuse")
    print(f" {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')} trace: {trace.id}")
    
except ImportError as e:
    print(f" Langfuse: {e}")
except Exception as e:
    print(f" : {e}")
    import traceback
    traceback.print_exc()