"""
报告生成智能体 - 生成详细的分析报告
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ..llm.manager import LLMManager
from ..llm.prompts import PromptManager
from ..tools.time_tool import time_tool

class ReportGenerator:
    """报告生成智能体"""
    
    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = "报告生成智能体"
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理报告生成请求"""
        query = data.get("query", "")
        search_results = data.get("search_results", [])
        synthesis_results = data.get("synthesis_results", {})
        report_type = data.get("report_type", "general")

        # 处理synthesis_results，转换为search_data格式
        if isinstance(synthesis_results, str):
            # 如果是字符串，直接包装
            search_data = {"all_content": [{"content": synthesis_results, "source": "synthesis"}]}
        elif isinstance(synthesis_results, dict) and synthesis_results:
            # 如果是字典，提取report_content或detailed_analysis
            content = synthesis_results.get("report_content") or synthesis_results.get("detailed_analysis", "")
            if content:
                search_data = {"all_content": [{"content": content, "source": "synthesis", **synthesis_results}]}
            elif "all_content" in synthesis_results:
                # 如果已经是正确格式
                search_data = synthesis_results
            else:
                # 没有可用内容，使用原始搜索结果
                search_data = {"all_content": search_results}
        else:
            # 空或无效，使用原始搜索结果
            search_data = {"all_content": search_results}

        result = await self.generate_report(query, search_data, report_type)
        return {
            "agent": self.name,
            "result": result,
            "status": "success" if result.get("report") else "failed"
        }
        
    async def generate_report(
        self, 
        query: str, 
        search_results: Dict[str, Any],
        report_type: str = "comprehensive",
        time_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """生成报告"""
        
        logger.info(f"[{self.name}] 开始生成 {report_type} 类型报告")
        
        # 获取时间上下文
        if not time_context:
            time_context = time_tool.parse_date_query(query)
        
        try:
            # 准备报告数据
            content_items = search_results.get("all_content", [])
            
            if not content_items:
                logger.warning(f"[{self.name}] 没有内容可用于生成报告")
                return self._generate_empty_report(query, report_type)
            
            # 根据报告类型选择模板
            report_template = self._get_report_template(report_type, time_context)
            
            # 构建报告生成提示
            report_prompt = self._build_report_prompt(
                query, content_items, report_template, time_context
            )
            
            # 调用LLM生成报告
            # 使用默认客户端进行简单聊天
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                report_prompt,
                "你是一个专业的报告生成专家，请按照要求生成详细报告。"
            )
            
            # 解析报告
            report = self._parse_report_response(response, report_type)
            
            # 添加元数据
            report["metadata"] = {
                "query": query,
                "report_type": report_type,
                "generation_time": datetime.now().isoformat(),
                "content_sources": len(content_items),
                "time_context": time_context,
                "word_count": len(report.get("content", ""))
            }
            
            logger.info(f"[{self.name}] 报告生成完成，字数: {report['metadata']['word_count']}")
            
            return {
                "report": report,
                "status": "success",
                "sources_used": len(content_items)
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] 报告生成失败: {e}")
            return {
                "report": self._generate_error_report(query, str(e)),
                "status": "error",
                "error": str(e)
            }
    
    def _get_report_template(self, report_type: str, time_context: Dict[str, Any]) -> str:
        """获取报告模板"""
        
        # 检查是否是日报类型
        if "日报" in report_type or "daily" in report_type.lower():
            template_name = "daily"
        elif "分析" in report_type or "analysis" in report_type.lower():
            template_name = "analysis"
        elif "研究" in report_type or "research" in report_type.lower():
            template_name = "research"
        else:
            template_name = "general"
        
        # 如果查询包含日期，优先使用日报模板
        if time_context.get("extracted_dates") and template_name == "general":
            template_name = "daily"
        
        return self.prompt_manager.get_prompt(
            f"agents/report_generator/{template_name}_system",
            default=self._get_default_template(template_name)
        )
    
    def _get_default_template(self, template_name: str) -> str:
        """获取默认模板"""
        templates = {
            "daily": """
# {title}

## 📅 日期概览
- 报告日期: {report_date}
- 涵盖时间: {time_range}

## 🔥 重点事件

{main_events}

## 📊 详细分析

{detailed_analysis}

## 🔗 重要链接

{important_links}

## 📝 总结

{summary}
            """,
            "analysis": """
# {title}

## 🎯 分析目标
{analysis_target}

## 📊 核心发现
{key_findings}

## 🔍 深度分析
{detailed_analysis}

## 💡 洞察与建议
{insights_recommendations}

## 📚 参考资料
{references}
            """,
            "research": """
# {title}

## 🔬 研究背景
{research_background}

## 📋 研究方法
{methodology}

## 📊 研究结果
{research_results}

## 🔍 结果分析
{result_analysis}

## 💭 结论与展望
{conclusions}

## 📖 参考文献
{references}
            """,
            "general": """
# {title}

## 📝 概述
{overview}

## 🔍 详细内容
{detailed_content}

## 💡 关键要点
{key_points}

## 🔗 相关资源
{related_resources}

## 📋 总结
{summary}
            """
        }
        
        return templates.get(template_name, templates["general"])
    
    def _build_report_prompt(
        self, 
        query: str, 
        content_items: List[Dict[str, Any]], 
        template: str,
        time_context: Dict[str, Any]
    ) -> str:
        """构建报告生成提示"""
        
        # 获取系统提示
        system_prompt = self.prompt_manager.get_prompt(
            "agents/report_generator/general_system",
            default="""你是一个专业的报告生成专家，负责基于搜索结果生成高质量的分析报告。

## 核心职责
1. 整合多个来源的信息，生成结构化报告
2. 确保报告内容准确、全面、有条理
3. 根据不同报告类型采用相应的格式和风格
4. 突出重点信息和关键洞察

## 报告要求
- 内容要详细、准确、有条理
- 严格按照时间要求筛选和组织内容
- 突出重点事件和关键信息
- 提供具体的数据和事实
- 包含相关的链接和来源
- 语言要专业但易懂"""
        )
        
        # 准备内容摘要
        content_summary = self._prepare_content_summary(content_items)
        
        # 时间信息
        time_info = time_context.get("time_context", "")
        extracted_dates = time_context.get("extracted_dates", [])
        current_time = time_context.get("current_time", {})
        
        prompt = f"""{system_prompt}

## 报告生成任务
用户查询: {query}

## 时间上下文
{time_info}
当前时间: {current_time.get('current_datetime', '未知')}
目标日期: {[d['formatted'] for d in extracted_dates] if extracted_dates else '无具体日期'}

## 内容来源
以下是从 {len(content_items)} 个来源收集的信息:

{content_summary}

## 报告模板
请严格按照以下模板格式生成报告:

{template}

## 生成要求
1. 报告内容要详细、准确、有条理
2. 严格按照时间要求筛选和组织内容
3. 突出重点事件和关键信息
4. 提供具体的数据和事实
5. 包含相关的链接和来源
6. 语言要专业但易懂
7. 如果是日报，要按时间顺序组织内容
8. 总字数应在2000-4000字之间

注意: 请确保所有内容都与指定的时间范围相关，过滤掉不相关的历史信息。
"""
        return prompt
    
    def _prepare_content_summary(self, content_items: List[Dict[str, Any]]) -> str:
        """准备内容摘要"""
        summaries = []
        
        for i, item in enumerate(content_items[:20]):  # 限制最多20个来源
            title = item.get("title", "无标题")
            url = item.get("url", "")
            content = item.get("content", "")[:500]  # 限制内容长度
            extracted_time = item.get("extracted_time", "未知时间")
            
            summary = f"""
来源 {i+1}:
标题: {title}
时间: {extracted_time}
URL: {url}
内容摘要: {content}...
---
"""
            summaries.append(summary)
        
        return "\n".join(summaries)
    
    def _parse_report_response(self, response: str, report_type: str) -> Dict[str, Any]:
        """解析报告响应"""
        try:
            # 提取标题
            title_match = response.split('\n')[0] if response else ""
            title = title_match.replace('#', '').strip() if title_match.startswith('#') else f"{report_type}报告"
            
            return {
                "title": title,
                "content": response,
                "type": report_type,
                "sections": self._extract_sections(response)
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] 解析报告响应时出错: {e}")
            return {
                "title": f"{report_type}报告",
                "content": response,
                "type": report_type,
                "sections": []
            }
    
    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """提取报告章节"""
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith('##'):
                # 保存上一个章节
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(current_content).strip()
                    })
                
                # 开始新章节
                current_section = line.replace('##', '').strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # 保存最后一个章节
        if current_section:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content).strip()
            })
        
        return sections
    
    def _generate_empty_report(self, query: str, report_type: str) -> Dict[str, Any]:
        """生成空报告"""
        return {
            "report": {
                "title": f"关于'{query}'的{report_type}报告",
                "content": f"抱歉，未能找到与查询'{query}'相关的内容。请尝试调整搜索关键词或扩大搜索范围。",
                "type": report_type,
                "sections": []
            },
            "status": "empty",
            "sources_used": 0
        }
    
    def _generate_error_report(self, query: str, error: str) -> Dict[str, Any]:
        """生成错误报告"""
        return {
            "title": f"报告生成失败",
            "content": f"在生成关于'{query}'的报告时发生错误: {error}",
            "type": "error",
            "sections": [],
            "metadata": {
                "generation_time": datetime.now().isoformat(),
                "error": error
            }
        }