"""
 - 
"""
import asyncio
from datetime import datetime
from loguru import logger

from src.llm.manager import LLMManager
from src.llm.prompts import PromptManager
from src.agents.coordinator_simple import SimpleCoordinator
from src.tools.time_tool import time_tool

async def main():
    """TODO: Add docstring."""
    
    # 
    logger.info("...")
    
    llm_manager = LLMManager()
    prompt_manager = PromptManager()
    coordinator = SimpleCoordinator(llm_manager, prompt_manager)
    
    # 
    system_status = coordinator.get_system_status()
    logger.info(f": {system_status}")
    
    # 
    current_time = time_tool.get_current_time()
    logger.info(f": {current_time['current_datetime']}")
    
    # 
    test_query = "2025924AIGCAI"
    
    logger.info(f": {test_query}")
    
    # 
    result = await coordinator.execute_deep_search(test_query, "daily")
    
    # 
    if result["status"] == "success":
        logger.info(" !")
        logger.info(f" :")
        stats = result.get("statistics", {})
        for key, value in stats.items():
            logger.info(f"  - {key}: {value}")
        
        if result.get("report_path"):
            logger.info(f" : {result['report_path']}")
        
        # 
        time_context = result.get("time_context", {})
        if time_context.get("extracted_dates"):
            logger.info(f" :")
            for date in time_context["extracted_dates"]:
                logger.info(f"  - : {date['formatted']}")
        
    else:
        logger.error(f" : {result.get('error', '')}")

if __name__ == "__main__":
    asyncio.run(main())