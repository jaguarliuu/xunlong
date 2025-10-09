#!/usr/bin/env python3
"""Langfuse API"""

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
    
    print(" Langfuse")
    
    # 
    try:
        langfuse.auth_check()
        print(" ")
    except Exception as e:
        print(f" : {e}")
    
    # trace - API
    trace = langfuse.trace(name="test-trace", input={"test": "data"})
    print(f" trace: {trace.id}")
    
    # generation - API
    generation = trace.generation(
        name="test-generation",
        model="test-model",
        input=[{"role": "user", "content": "Hello"}],
        output="Hi there!"
    )
    print(f" generation: {generation.id}")
    
    # span - API
    span = trace.span(
        name="test-span",
        input={"action": "test"},
        output={"result": "success"}
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