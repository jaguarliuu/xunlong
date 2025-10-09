#!/usr/bin/env python3
"""TODO: Add docstring."""

import os
import time
from dotenv import load_dotenv
load_dotenv()

# 
from src.monitoring.langfuse_monitor import monitor

def test_monitor_integration():
    """TODO: Add docstring."""
    print(" Langfuse...")
    
    if not monitor.enabled:
        print(" ")
        return False
    
    print(" ")
    
    # trace
    trace_id = monitor.start_trace(
        name="DeepSearch-Integration-Test",
        input_data={"query": "", "mode": "integration_test"},
        metadata={"version": "1.0.0", "test": True}
    )
    
    if not trace_id:
        print(" trace")
        return False
    
    print(f" trace: {trace_id}")
    
    # LLM
    generation_id = monitor.log_llm_call(
        trace_id=trace_id,
        model="qwen-turbo",
        input_messages=[{"role": "user", "content": "Hello"}],
        output="Hi there!",
        usage={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
        metadata={"temperature": 0.7}
    )
    
    if generation_id:
        print(f" LLM: {generation_id}")
        # LLM
        monitor.end_llm_call(generation_id, output="Final response", usage={"total_tokens": 10})
    else:
        print(" LLM")
    
    # Agent
    span_id = monitor.log_agent_action(
        trace_id=trace_id,
        agent_name="TestAgent",
        action="test_action",
        input_data={"action": "test"},
        metadata={"start_time": time.time()}
    )
    
    if span_id:
        print(f" Agent: {span_id}")
        # Agent
        monitor.end_agent_action(span_id, output_data={"result": "success"}, metadata={"duration": 1.5})
    else:
        print(" Agent")
    
    # 
    monitor.log_search_action(
        trace_id=trace_id,
        query="",
        results_count=10,
        search_time=2.5,
        metadata={"search_engine": "duckduckgo"}
    )
    print(" ")
    
    # 
    monitor.log_content_extraction(
        trace_id=trace_id,
        url="https://example.com",
        content_length=1500,
        extraction_time=1.2,
        success=True,
        metadata={"method": "playwright"}
    )
    print(" ")
    
    # 
    event_id = monitor.log_event(
        trace_id=trace_id,
        name="test-completed",
        input_data={"status": "success"},
        metadata={"timestamp": time.time()}
    )
    
    if event_id:
        print(f" : {event_id}")
    else:
        print(" ")
    
    # trace
    monitor.end_trace(
        trace_id=trace_id,
        output_data={"status": "completed", "test": True},
        metadata={"total_time": 5.0}
    )
    print(" trace")
    
    # 
    monitor.flush()
    print(" ")
    
    print(f"  {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')} trace: {trace_id}")
    return True

if __name__ == "__main__":
    success = test_monitor_integration()
    if success:
        print(" ")
    else:
        print(" ")