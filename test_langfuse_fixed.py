#!/usr/bin/env python3
"""测试修复后的Langfuse API"""

import os
import time
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
    langfuse.auth_check()
    print("✅ 认证成功")
    
    # 创建trace ID
    trace_id = f"test-trace-{int(time.time())}"
    print(f"使用trace ID: {trace_id}")
    
    # 创建事件作为trace开始
    event = langfuse.create_event(
        trace_id=trace_id,
        name="trace-start-test",
        input={"test": "data"},
        metadata={"version": "1.0.0"}
    )
    print(f"✅ 创建事件成功: {event.id}")
    
    # 创建generation (LLM调用)
    generation = langfuse.start_generation(
        trace_id=trace_id,
        name="LLM-test-model",
        model="test-model",
        input=[{"role": "user", "content": "Hello"}],
        output="Hi there!",
        usage={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
        metadata={"test": True}
    )
    print(f"✅ 创建generation成功: {generation.id}")
    
    # 创建span (Agent动作)
    span = langfuse.start_span(
        trace_id=trace_id,
        name="Agent-TestAgent-test_action",
        input={"action": "test"},
        output={"result": "success"},
        metadata={"duration": 1.5}
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
    import traceback
    traceback.print_exc()