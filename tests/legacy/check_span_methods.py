#!/usr/bin/env python3
"""LangfuseSpan"""

import os
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
    
    # span
    span = langfuse.start_observation(
        name="test-span",
        as_type="span"
    )
    
    print("LangfuseSpan:")
    for attr in dir(span):
        if not attr.startswith('_'):
            print(f"  {attr}")
    
    print(f"\nspan: {type(span)}")
    print(f"span.id: {span.id}")
    
    # trace
    if hasattr(span, 'trace_id'):
        print(f"span.trace_id: {span.trace_id}")
    if hasattr(span, 'trace'):
        print(f"span.trace: {span.trace}")
    if hasattr(span, 'get_trace_id'):
        print(f"span.get_trace_id(): {span.get_trace_id()}")
        
    span.end()
    
except Exception as e:
    print(f": {e}")
    import traceback
    traceback.print_exc()