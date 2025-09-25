"""内容综合智能体"""

import json
from typing import Dict, Any, List
from loguru import logger

from .base import BaseAgent, AgentConfig
from ..llm import LLMManager, PromptManager


class ContentSynthesizerAgent(BaseAgent):
    """内容综合智能体 - 整合多源信息，生成连贯报告"""
    
    def __init__(
        self, 
        llm_manager: LLMManager,
        prompt_manager: PromptManager = None
    ):
        config = AgentConfig(
            name="内容综合智能体",
            description="整合搜索结果和分析，生成连贯的综合报告",
            llm_config_name="content_synthesizer",
            temperature=0.7,
            max_tokens=6000
        )
        
        super().__init__(llm_manager, prompt_manager, config)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理内容综合"""
        try:
            query = input_data.get("query", "")
            search_results = input_data.get("search_results", [])
            analysis_results = input_data.get("analysis_results", {})
            
            logger.info(f"开始内容综合: {query}")
            
            # 获取系统提示词
            system_prompt = self.get_prompt("agents/content_synthesizer/system")
            
            # 准备综合信息
            synthesis_data = {
                "query": query,
                "search_results_count": len(search_results),
                "key_insights": analysis_results.get("result", {}).get("key_insights", []),
                "content_themes": analysis_results.get("result", {}).get("content_themes", []),
                "top_results": []
            }
            
            # 提取前3个最相关的搜索结果
            for i, result in enumerate(search_results[:3]):
                synthesis_data["top_results"].append({
                    "title": result.get("title", "无标题"),
                    "url": result.get("url", ""),
                    "content_summary": result.get("content", "")[:500] + "..." if result.get("content") else "无内容"
                })
            
            # 构建用户提示词
            user_prompt = f"""
请基于以下信息，为查询"{query}"生成一份综合报告：

综合信息:
{json.dumps(synthesis_data, ensure_ascii=False, indent=2)}

请生成一份结构化的报告，包含：
1. 执行摘要
2. 主要发现
3. 详细分析
4. 结论和建议
5. 信息来源

报告应该连贯、准确、有洞察力。请以JSON格式返回，包含report_content字段。
"""
            
            # 获取LLM响应
            response = await self.get_llm_response(user_prompt, system_prompt)
            
            # 尝试解析JSON响应
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # 如果JSON解析失败，将响应作为报告内容
                result = {
                    "report_content": response,
                    "executive_summary": "基于搜索结果生成的综合报告",
                    "main_findings": ["找到相关信息"],
                    "detailed_analysis": response,
                    "conclusions": ["信息综合完成"],
                    "sources": [r.get("url", "") for r in search_results[:3]]
                }
            
            # 确保包含必要字段
            if "report_content" not in result:
                result["report_content"] = result.get("detailed_analysis", response)
            
            # 添加元数据
            result["query"] = query
            result["synthesis_timestamp"] = "2025-09-25"  # 简化时间戳
            result["sources_count"] = len(search_results)
            result["analysis_quality"] = "good" if analysis_results.get("status") == "success" else "limited"
            
            logger.info(f"内容综合完成: 生成了 {len(result.get('report_content', ''))} 字符的报告")
            
            return {
                "status": "success",
                "agent": self.name,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"内容综合失败: {e}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e),
                "result": {
                    "report_content": f"抱歉，无法生成关于'{input_data.get('query', '')}'的综合报告。错误: {e}",
                    "executive_summary": "报告生成失败",
                    "main_findings": [],
                    "detailed_analysis": "分析过程中出现错误",
                    "conclusions": ["请重试或联系技术支持"],
                    "sources": [],
                    "query": input_data.get("query", ""),
                    "sources_count": 0,
                    "analysis_quality": "failed"
                }
            }