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
    print(":")
    methods = [method for method in dir(langfuse) if not method.startswith('_')]
    for method in sorted(methods):
        print(f"  - {method}")
    
    # 
    try:
        langfuse.auth_check()
        print(" ")
    except Exception as e:
        print(f" : {e}")
    
    # API
    print("\ntrace...")
    
    # 1: 
    try:
        if hasattr(langfuse, 'trace'):
            trace = langfuse.trace(name="test-trace")
            print(" 1: langfuse.trace()")
        else:
            print(" 1: trace")
    except Exception as e:
        print(f" 1: {e}")
    
    # 2: create_trace
    try:
        if hasattr(langfuse, 'create_trace'):
            trace = langfuse.create_trace(name="test-trace")
            print(" 2: langfuse.create_trace()")
        else:
            print(" 2: create_trace")
    except Exception as e:
        print(f" 2: {e}")
    
    # 3: trace
    try:
        if hasattr(langfuse, 'trace'):
            trace = langfuse.trace()
            trace.update(name="test-trace")
            print(" 3: langfuse.trace().update()")
        else:
            print(" 3: trace")
    except Exception as e:
        print(f" 3: {e}")
        
except ImportError as e:
    print(f" Langfuse: {e}")
except Exception as e:
    print(f" : {e}")