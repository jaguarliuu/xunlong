#!/usr/bin/env python3
"""检查create_event的正确参数"""

import inspect
from dotenv import load_dotenv
load_dotenv()

try:
    from langfuse import Langfuse
    
    # 检查create_event方法的签名
    print("create_event方法签名:")
    print(inspect.signature(Langfuse.create_event))
    
    # 检查start_observation方法的签名
    print("\nstart_observation方法签名:")
    print(inspect.signature(Langfuse.start_observation))
    
    # 检查start_generation方法的签名
    print("\nstart_generation方法签名:")
    print(inspect.signature(Langfuse.start_generation))
    
    # 检查start_span方法的签名
    print("\nstart_span方法签名:")
    print(inspect.signature(Langfuse.start_span))
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()