#!/usr/bin/env python3
"""测试正确的Langfuse API用法"""

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
    
    # 创建trace (使用start_observation作为trace根节点)
    trace = langfuse.start_observation(
        name="DeepSearch-Test-Trace",
        as_type="span",
        input={"query": "测试查询"},
        metadata={"version": "1.0.0", "test": True}
    )
    print(f"✅ 创建trace成功: {trace.id}")
    
    # 创建generation (LLM调用) - 作为trace的子节点
    generation = langfuse.start_generation(
        trace_context=trace.get_trace_context(),
        name="LLM-Qianwen-Call",
        model="qwen-turbo",
        input=[{"role": "user", "content": "Hello"}],
        output="Hi there!",
        usage_details={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
        metadata={"temperature": 0.7}
    )
    print(f"✅ 创建generation成功: {generation.id}")
    
    # 创建span (Agent动作) - 作为trace的子节点
    span = langfuse.start_span(
        trace_context=trace.get_trace_context(),
        name="Agent-DeepSearcher-search",
        input={"query": "测试搜索", "max_results": 10},
        output={"results_count": 5, "status": "success"},
        metadata={"duration": 2.5, "search_engine": "duckduckgo"}
    )
    print(f"✅ 创建span成功: {span.id}")
    
    # 创建事件 - 作为trace的子节点
    event = langfuse.create_event(
        trace_context=trace.get_trace_context(),
        name="search-completed",
        input={"query": "测试查询"},
        metadata={"timestamp": time.time()}
    )
    print(f"✅ 创建event成功: {event.id}")
    
    # 结束所有观察
    generation.end()
    span.end()
    trace.end()
    
    # 刷新数据
    langfuse.flush()
    print("✅ 数据已发送到Langfuse")
    print(f"请访问 {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')} 查看trace: {trace.id}")
    
except ImportError as e:
    print(f"❌ 导入Langfuse失败: {e}")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()