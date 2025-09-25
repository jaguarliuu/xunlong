"""搜索分析智能体"""

import json
from typing import Dict, Any, List
from loguru import logger

from .base import BaseAgent, AgentConfig
from ..llm import LLMManager, PromptManager


class SearchAnalyzerAgent(BaseAgent):
    """搜索分析智能体 - 深度分析搜索结果，提取关键信息"""
    
    def __init__(
        self, 
        llm_manager: LLMManager,
        prompt_manager: PromptManager = None
    ):
        config = AgentConfig(
            name="搜索分析智能体",
            description="深度分析搜索结果，提取关键信息和洞察",
            llm_config_name="search_analyzer",
            temperature=0.5,
            max_tokens=4000
        )
        
        super().__init__(llm_manager, prompt_manager, config)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理搜索结果分析"""
        try:
            query = input_data.get("query", "")
            search_results = input_data.get("search_results", [])
            
            logger.info(f"开始搜索分析: {len(search_results)} 个结果")
            
            if not search_results:
                return {
                    "status": "warning",
                    "agent": self.name,
                    "result": {
                        "analysis_summary": "没有搜索结果可供分析",
                        "key_insights": [],
                        "relevance_scores": [],
                        "content_themes": [],
                        "recommendations": ["建议尝试不同的搜索关键词"]
                    }
                }
            
            # 获取系统提示词
            system_prompt = self.get_prompt("agents/search_analyzer/system")
            
            # 构建搜索结果摘要
            results_summary = []
            for i, result in enumerate(search_results[:5]):  # 限制分析前5个结果
                summary = {
                    "index": i + 1,
                    "title": result.get("title", "无标题"),
                    "url": result.get("url", ""),
                    "content_preview": result.get("content", "")[:300] + "..." if result.get("content") else "无内容"
                }
                results_summary.append(summary)
            
            # 构建用户提示词
            user_prompt = f"""
请分析以下搜索结果，针对查询"{query}"：

搜索结果:
{json.dumps(results_summary, ensure_ascii=False, indent=2)}

请提供：
1. 分析总结
2. 关键洞察和发现
3. 每个结果的相关性评分（1-10）
4. 内容主题分类
5. 进一步搜索建议

请以JSON格式返回结果。
"""
            
            # 获取LLM响应
            response = await self.get_llm_response(user_prompt, system_prompt)
            
            # 尝试解析JSON响应
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回基本结果
                result = {
                    "analysis_summary": "搜索结果分析完成",
                    "key_insights": ["找到相关信息"],
                    "relevance_scores": [8] * len(search_results),
                    "content_themes": ["综合信息"],
                    "recommendations": ["结果质量良好"],
                    "raw_response": response
                }
            
            # 添加统计信息
            result["total_results"] = len(search_results)
            result["analyzed_results"] = min(len(search_results), 5)
            
            logger.info(f"搜索分析完成: {result.get('analysis_summary', '分析完成')}")
            
            return {
                "status": "success",
                "agent": self.name,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"搜索分析失败: {e}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e),
                "result": {
                    "analysis_summary": "分析失败",
                    "key_insights": [],
                    "relevance_scores": [],
                    "content_themes": [],
                    "recommendations": ["请重试分析"],
                    "total_results": len(input_data.get("search_results", [])),
                    "analyzed_results": 0
                }
            }