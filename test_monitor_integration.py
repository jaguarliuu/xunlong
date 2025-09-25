#!/usr/bin/env python3
"""测试修复后的监控集成"""

import os
import time
from dotenv import load_dotenv
load_dotenv()

# 导入修复后的监控器
from src.monitoring.langfuse_monitor import monitor

def test_monitor_integration():
    """测试监控器集成"""
    print("🔍 测试Langfuse监控集成...")
    
    if not monitor.enabled:
        print("❌ 监控器未启用")
        return False
    
    print("✅ 监控器已启用")
    
    # 开始一个trace
    trace_id = monitor.start_trace(
        name="DeepSearch-Integration-Test",
        input_data={"query": "测试查询", "mode": "integration_test"},
        metadata={"version": "1.0.0", "test": True}
    )
    
    if not trace_id:
        print("❌ 创建trace失败")
        return False
    
    print(f"✅ 创建trace成功: {trace_id}")
    
    # 记录LLM调用
    generation_id = monitor.log_llm_call(
        trace_id=trace_id,
        model="qwen-turbo",
        input_messages=[{"role": "user", "content": "Hello"}],
        output="Hi there!",
        usage={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
        metadata={"temperature": 0.7}
    )
    
    if generation_id:
        print(f"✅ 记录LLM调用成功: {generation_id}")
        # 结束LLM调用
        monitor.end_llm_call(generation_id, output="Final response", usage={"total_tokens": 10})
    else:
        print("❌ 记录LLM调用失败")
    
    # 记录Agent动作
    span_id = monitor.log_agent_action(
        trace_id=trace_id,
        agent_name="TestAgent",
        action="test_action",
        input_data={"action": "test"},
        metadata={"start_time": time.time()}
    )
    
    if span_id:
        print(f"✅ 记录Agent动作成功: {span_id}")
        # 结束Agent动作
        monitor.end_agent_action(span_id, output_data={"result": "success"}, metadata={"duration": 1.5})
    else:
        print("❌ 记录Agent动作失败")
    
    # 记录搜索动作
    monitor.log_search_action(
        trace_id=trace_id,
        query="测试搜索",
        results_count=10,
        search_time=2.5,
        metadata={"search_engine": "duckduckgo"}
    )
    print("✅ 记录搜索动作")
    
    # 记录内容提取
    monitor.log_content_extraction(
        trace_id=trace_id,
        url="https://example.com",
        content_length=1500,
        extraction_time=1.2,
        success=True,
        metadata={"method": "playwright"}
    )
    print("✅ 记录内容提取")
    
    # 记录事件
    event_id = monitor.log_event(
        trace_id=trace_id,
        name="test-completed",
        input_data={"status": "success"},
        metadata={"timestamp": time.time()}
    )
    
    if event_id:
        print(f"✅ 记录事件成功: {event_id}")
    else:
        print("❌ 记录事件失败")
    
    # 结束trace
    monitor.end_trace(
        trace_id=trace_id,
        output_data={"status": "completed", "test": True},
        metadata={"total_time": 5.0}
    )
    print("✅ 结束trace")
    
    # 刷新数据
    monitor.flush()
    print("✅ 数据已刷新")
    
    print(f"🎉 测试完成！请访问 {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')} 查看trace: {trace_id}")
    return True

if __name__ == "__main__":
    success = test_monitor_integration()
    if success:
        print("✅ 监控集成测试成功")
    else:
        print("❌ 监控集成测试失败")