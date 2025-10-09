"""TODO: Add docstring."""

import json
from typing import Dict, Any
from loguru import logger

from .base import BaseAgent, AgentConfig
from ..llm import LLMManager, PromptManager


class QueryOptimizerAgent(BaseAgent):
    """ - """
    
    def __init__(
        self, 
        llm_manager: LLMManager,
        prompt_manager: PromptManager = None
    ):
        config = AgentConfig(
            name="",
            description="",
            llm_config_name="query_optimizer",
            temperature=0.3,
            max_tokens=2000
        )
        
        super().__init__(llm_manager, prompt_manager, config)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """TODO: Add docstring."""
        try:
            query = input_data.get("query", "")
            context = input_data.get("context", {})
            
            logger.info(f": {query}")
            
            # 
            system_prompt = self.get_prompt("agents/query_optimizer/system")
            
            # 
            user_prompt = f"""


: {query}


1. 
2. 
3. 
4. 

JSON
"""
            
            # LLM
            response = await self.get_llm_response(user_prompt, system_prompt)
            
            # JSON
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # JSON
                result = {
                    "intent_analysis": "",
                    "optimized_keywords": [query],
                    "search_strategy": "",
                    "expected_result_type": "",
                    "raw_response": response
                }
            
            # 
            result["original_query"] = query
            result["optimized_query"] = result.get("optimized_keywords", [query])[0] if result.get("optimized_keywords") else query
            
            logger.info(f": {result.get('optimized_query', query)}")
            
            return {
                "status": "success",
                "agent": self.name,
                "result": result
            }
            
        except Exception as e:
            logger.error(f": {e}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e),
                "result": {
                    "original_query": input_data.get("query", ""),
                    "optimized_query": input_data.get("query", ""),
                    "intent_analysis": "",
                    "optimized_keywords": [input_data.get("query", "")],
                    "search_strategy": "",
                    "expected_result_type": ""
                }
            }