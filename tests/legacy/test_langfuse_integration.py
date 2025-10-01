#!/usr/bin/env python3
"""测试Langfuse集成"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from src.monitoring.langfuse_monitor import monitor
from loguru import logger

def test_langfuse_connection():
    """测试Langfuse连接"""
    logger.info("=== 测试Langfuse集成 ===")
    
    # 检查环境变量
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    public_key = os.getenv("LANGFUSE_PUB_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    logger.info(f"LANGFUSE_SECRET_KEY: {'已设置' if secret_key else '未设置'}")
    logger.info(f"LANGFUSE_PUB_KEY: {'已设置' if public_key else '未设置'}")
    logger.info(f"LANGFUSE_HOST: {host}")
    
    # 检查监控器状态
    logger.info(f"监控器启用状态: {monitor.enabled}")
    
    if not monitor.enabled:
        logger.error("Langfuse监控未启用，请检查配置")
        return False
    
    # 创建测试追踪
    try:
        trace_id = f"test-trace-{int(time.time())}"
        logger.info(f"创建测试追踪: {trace_id}")
        
        # 开始追踪
        monitor.start_trace(
            trace_id=trace_id,
            name="Langfuse集成测试",
            input_data={"test": "integration"},
            metadata={"version": "1.0.0", "environment": "test"}
        )
        
        # 记录一个LLM调用
        monitor.log_llm_call(
            trace_id=trace_id,
            model="test-model",
            input_messages=[{"role": "user", "content": "测试消息"}],
            output="测试响应",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            metadata={"test": True}
        )
        
        # 记录Agent动作
        monitor.log_agent_action(
            trace_id=trace_id,
            agent_name="TestAgent",
            action="test_action",
            input_data={"input": "test"},
            output_data={"output": "success"},
            metadata={"duration": 1.5}
        )
        
        # 结束追踪
        monitor.end_trace(
            trace_id=trace_id,
            output_data={"result": "success"},
            metadata={"total_duration": 2.0}
        )
        
        # 刷新缓冲区
        monitor.flush()
        
        logger.success("✅ Langfuse集成测试成功！")
        logger.info(f"请访问 {host} 查看追踪记录")
        return True
        
    except Exception as e:
        logger.error(f"❌ Langfuse集成测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_langfuse_connection()
    sys.exit(0 if success else 1)