#!/usr/bin/env python3
"""简单的Langfuse API测试"""

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
    
    # 测试认证
    try:
        langfuse.auth_check()
        print("✅ 认证成功")
    except Exception as e:
        print(f"❌ 认证失败: {e}")
    
    # 创建一个简单的trace - 使用正确的API
    trace = langfuse.trace(name="test-trace", input={"test": "data"})
    print(f"✅ 创建trace成功: {trace.id}")
    
    # 创建一个generation - 使用正确的API
    generation = trace.generation(
        name="test-generation",
        model="test-model",
        input=[{"role": "user", "content": "Hello"}],
        output="Hi there!"
    )
    print(f"✅ 创建generation成功: {generation.id}")
    
    # 创建一个span - 使用正确的API
    span = trace.span(
        name="test-span",
        input={"action": "test"},
        output={"result": "success"}
    )
    print(f"✅ 创建span成功: {span.id}")
    
    # 刷新数据
    langfuse.flush()
    print("✅ 数据已发送到Langfuse")
    print(f"请访问 {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')} 查看数据")
    
except ImportError as e:
    print(f"❌ 导入Langfuse失败: {e}")
except Exception as e:
    print(f"❌ 测试失败: {e}")