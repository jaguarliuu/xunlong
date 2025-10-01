#!/usr/bin/env python3
"""检查Langfuse API"""

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
    
    print("✅ Langfuse客户端初始化成功")
    print("可用方法:")
    methods = [method for method in dir(langfuse) if not method.startswith('_')]
    for method in sorted(methods):
        print(f"  - {method}")
    
    # 测试认证
    try:
        langfuse.auth_check()
        print("✅ 认证成功")
    except Exception as e:
        print(f"❌ 认证失败: {e}")
    
    # 尝试不同的API调用方式
    print("\n尝试创建trace...")
    
    # 方式1: 直接调用
    try:
        if hasattr(langfuse, 'trace'):
            trace = langfuse.trace(name="test-trace")
            print("✅ 方式1成功: langfuse.trace()")
        else:
            print("❌ 方式1失败: 没有trace方法")
    except Exception as e:
        print(f"❌ 方式1失败: {e}")
    
    # 方式2: 使用create_trace
    try:
        if hasattr(langfuse, 'create_trace'):
            trace = langfuse.create_trace(name="test-trace")
            print("✅ 方式2成功: langfuse.create_trace()")
        else:
            print("❌ 方式2失败: 没有create_trace方法")
    except Exception as e:
        print(f"❌ 方式2失败: {e}")
    
    # 方式3: 使用trace方法但不同参数
    try:
        if hasattr(langfuse, 'trace'):
            trace = langfuse.trace()
            trace.update(name="test-trace")
            print("✅ 方式3成功: langfuse.trace().update()")
        else:
            print("❌ 方式3失败: 没有trace方法")
    except Exception as e:
        print(f"❌ 方式3失败: {e}")
        
except ImportError as e:
    print(f"❌ 导入Langfuse失败: {e}")
except Exception as e:
    print(f"❌ 测试失败: {e}")