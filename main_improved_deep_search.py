"""
改进版深度搜索系统演示 - 集成时间工具和内容评估
"""
import asyncio
from datetime import datetime
from loguru import logger

from src.llm.manager import LLMManager
from src.llm.prompts import PromptManager
from src.agents.coordinator_simple import SimpleCoordinator
from src.tools.time_tool import time_tool

async def main():
    """主函数"""
    
    # 初始化系统
    logger.info("初始化改进版深度搜索系统...")
    
    llm_manager = LLMManager()
    prompt_manager = PromptManager()
    coordinator = SimpleCoordinator(llm_manager, prompt_manager)
    
    # 显示系统状态
    system_status = coordinator.get_system_status()
    logger.info(f"系统状态: {system_status}")
    
    # 显示当前时间
    current_time = time_tool.get_current_time()
    logger.info(f"当前时间: {current_time['current_datetime']}")
    
    # 测试查询
    test_query = "获取2025年9月24日AIGC领域发生的大事件，输出AI日报"
    
    logger.info(f"开始处理查询: {test_query}")
    
    # 执行深度搜索
    result = await coordinator.execute_deep_search(test_query, "daily")
    
    # 显示结果
    if result["status"] == "success":
        logger.info("✅ 深度搜索成功完成!")
        logger.info(f"📊 统计信息:")
        stats = result.get("statistics", {})
        for key, value in stats.items():
            logger.info(f"  - {key}: {value}")
        
        if result.get("report_path"):
            logger.info(f"📄 报告已保存到: {result['report_path']}")
        
        # 显示时间上下文验证
        time_context = result.get("time_context", {})
        if time_context.get("extracted_dates"):
            logger.info(f"🕒 时间解析结果:")
            for date in time_context["extracted_dates"]:
                logger.info(f"  - 目标日期: {date['formatted']}")
        
    else:
        logger.error(f"❌ 深度搜索失败: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    asyncio.run(main())