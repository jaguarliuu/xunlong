#!/usr/bin/env python3
"""检查LangfuseSpan对象的可用方法"""

import os
from dotenv import load_dotenv
load_dotenv()

try:
    from langfuse import Langfuse
    
    # 初始化客户端
    langfuse = Langfuse(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUB_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    
    # 创建一个span
    span = langfuse.start_observation(
        name="test-span",
        as_type="span"
    )
    
    print("LangfuseSpan对象的所有属性和方法:")
    for attr in dir(span):
        if not attr.startswith('_'):
            print(f"  {attr}")
    
    print(f"\nspan对象类型: {type(span)}")
    print(f"span.id: {span.id}")
    
    # 检查是否有trace相关属性
    if hasattr(span, 'trace_id'):
        print(f"span.trace_id: {span.trace_id}")
    if hasattr(span, 'trace'):
        print(f"span.trace: {span.trace}")
    if hasattr(span, 'get_trace_id'):
        print(f"span.get_trace_id(): {span.get_trace_id()}")
        
    span.end()
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()