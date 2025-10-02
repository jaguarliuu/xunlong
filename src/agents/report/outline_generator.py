"""
大纲生成智能体 - 生成结构化的报告大纲
"""
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
import json
import re

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager


class OutlineGenerator:
    """大纲生成智能体"""

    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = "大纲生成器"

    async def generate_outline(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        synthesis_results: Optional[Dict[str, Any]] = None,
        report_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """生成报告大纲"""

        logger.info(f"[{self.name}] 开始生成报告大纲 (类型: {report_type})")

        try:
            # 构建大纲生成提示
            outline_prompt = self._build_outline_prompt(
                query, search_results, synthesis_results, report_type
            )

            # 调用LLM生成大纲
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                outline_prompt,
                "你是一个专业的报告大纲设计专家，擅长设计结构化、逻辑清晰的报告大纲。"
            )

            # 解析大纲
            outline = self._parse_outline_response(response)

            # 验证和优化大纲
            outline = self._validate_and_optimize_outline(outline, report_type)

            logger.info(f"[{self.name}] 大纲生成完成，共 {len(outline['sections'])} 个段落")

            return {
                "outline": outline,
                "total_sections": len(outline["sections"]),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"[{self.name}] 大纲生成失败: {e}")
            return {
                "outline": self._get_fallback_outline(report_type),
                "total_sections": 0,
                "status": "error",
                "error": str(e)
            }

    def _build_outline_prompt(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        synthesis_results: Optional[Dict[str, Any]],
        report_type: str
    ) -> str:
        """构建大纲生成提示"""

        # 准备搜索结果摘要
        results_summary = self._summarize_search_results(search_results[:10])

        # 准备综合结果摘要
        synthesis_summary = ""
        if synthesis_results:
            if isinstance(synthesis_results, dict):
                synthesis_summary = synthesis_results.get("report_content", "")[:500]
            elif isinstance(synthesis_results, str):
                synthesis_summary = synthesis_results[:500]

        prompt = f"""# 报告大纲生成任务

## 用户查询
{query}

## 报告类型
{report_type}

## 可用信息摘要
### 搜索结果 ({len(search_results)} 个来源)
{results_summary}

### 内容综合
{synthesis_summary}

## 任务要求

请设计一个结构化的报告大纲，包含以下要素：

1. **报告标题**: 准确反映主题
2. **段落结构**: 3-6 个主要段落（section）
3. **每个段落包含**:
   - id: 段落编号（从1开始）
   - title: 段落标题
   - requirements: 本段应包含的核心内容（详细描述）
   - suggested_sources: 推荐使用的信息源标题（从搜索结果中选择）
   - word_count: 建议字数
   - importance: 重要性权重（0.0-1.0）

## 报告类型指南

- **comprehensive** (综合报告): 全面、深入的分析报告
  - 结构: 引言 → 背景 → 核心内容 → 详细分析 → 总结
  - 字数: 每段 500-800 字

- **daily** (日报): 简洁的每日资讯汇总
  - 结构: 概览 → 重点事件 → 详细分析 → 总结
  - 字数: 每段 300-500 字

- **analysis** (分析报告): 针对性的深度分析
  - 结构: 问题定义 → 数据分析 → 关键发现 → 结论建议
  - 字数: 每段 400-600 字

- **research** (研究报告): 学术级别的研究文档
  - 结构: 摘要 → 引言 → 方法 → 结果 → 讨论 → 结论
  - 字数: 每段 600-1000 字

## 输出格式

请严格按照以下JSON格式输出:

```json
{{
  "title": "报告标题",
  "sections": [
    {{
      "id": 1,
      "title": "段落标题",
      "requirements": "详细描述本段应包含的核心内容、论点、数据等",
      "suggested_sources": ["来源1标题", "来源2标题"],
      "word_count": 500,
      "importance": 0.9
    }}
  ]
}}
```

注意:
- 段落之间应有逻辑连贯性
- requirements 要具体明确，便于写作智能体理解
- 建议字数要合理，符合报告类型
- 重要性权重总和应接近段落数量
"""

        return prompt

    def _summarize_search_results(self, results: List[Dict[str, Any]]) -> str:
        """总结搜索结果"""
        if not results:
            return "暂无搜索结果"

        summaries = []
        for i, result in enumerate(results[:10], 1):
            title = result.get("title", "无标题")
            url = result.get("url", "")
            content_preview = result.get("content", "")[:100]

            summaries.append(f"{i}. {title}\n   来源: {url}\n   摘要: {content_preview}...")

        return "\n\n".join(summaries)

    def _parse_outline_response(self, response: str) -> Dict[str, Any]:
        """解析大纲响应"""
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                outline = json.loads(json_str)

                # 验证必要字段
                if "title" in outline and "sections" in outline:
                    return outline

            logger.warning(f"[{self.name}] JSON解析失败，使用默认大纲")
            return self._get_fallback_outline("comprehensive")

        except Exception as e:
            logger.error(f"[{self.name}] 解析大纲响应失败: {e}")
            return self._get_fallback_outline("comprehensive")

    def _validate_and_optimize_outline(
        self,
        outline: Dict[str, Any],
        report_type: str
    ) -> Dict[str, Any]:
        """验证和优化大纲"""

        sections = outline.get("sections", [])

        # 确保段落数量合理
        if len(sections) < 3:
            logger.warning(f"[{self.name}] 段落数量过少 ({len(sections)})，添加默认段落")
            sections = self._add_missing_sections(sections, report_type)

        if len(sections) > 6:
            logger.warning(f"[{self.name}] 段落数量过多 ({len(sections)})，保留前6个")
            sections = sections[:6]

        # 验证每个段落的必要字段
        for i, section in enumerate(sections):
            # 确保有id
            if "id" not in section:
                section["id"] = i + 1

            # 确保有标题
            if "title" not in section or not section["title"]:
                section["title"] = f"第{i+1}部分"

            # 确保有要求
            if "requirements" not in section or not section["requirements"]:
                section["requirements"] = f"撰写关于{outline.get('title', '主题')}的{section['title']}部分"

            # 确保有建议字数
            if "word_count" not in section:
                section["word_count"] = 500

            # 确保有重要性
            if "importance" not in section:
                section["importance"] = 1.0 / len(sections)

            # 确保有建议来源（可为空）
            if "suggested_sources" not in section:
                section["suggested_sources"] = []

        outline["sections"] = sections

        return outline

    def _add_missing_sections(
        self,
        sections: List[Dict[str, Any]],
        report_type: str
    ) -> List[Dict[str, Any]]:
        """添加缺失的段落"""

        default_sections = {
            "comprehensive": ["引言", "背景分析", "核心内容", "详细讨论", "总结"],
            "daily": ["今日概览", "重点事件", "详细分析", "总结"],
            "analysis": ["问题定义", "数据分析", "关键发现", "结论建议"],
            "research": ["摘要", "引言", "研究方法", "研究结果", "讨论", "结论"]
        }

        template = default_sections.get(report_type, default_sections["comprehensive"])

        # 如果现有段落为空，使用模板
        if not sections:
            return [
                {
                    "id": i + 1,
                    "title": title,
                    "requirements": f"撰写{title}部分的内容",
                    "word_count": 500,
                    "importance": 1.0 / len(template),
                    "suggested_sources": []
                }
                for i, title in enumerate(template)
            ]

        return sections

    def _get_fallback_outline(self, report_type: str) -> Dict[str, Any]:
        """获取备用大纲"""

        default_outlines = {
            "comprehensive": {
                "title": "综合分析报告",
                "sections": [
                    {
                        "id": 1,
                        "title": "引言",
                        "requirements": "介绍报告背景、目的和结构",
                        "word_count": 300,
                        "importance": 0.15,
                        "suggested_sources": []
                    },
                    {
                        "id": 2,
                        "title": "核心内容",
                        "requirements": "呈现主要发现和关键信息",
                        "word_count": 800,
                        "importance": 0.35,
                        "suggested_sources": []
                    },
                    {
                        "id": 3,
                        "title": "详细分析",
                        "requirements": "深入分析数据和趋势",
                        "word_count": 700,
                        "importance": 0.30,
                        "suggested_sources": []
                    },
                    {
                        "id": 4,
                        "title": "总结",
                        "requirements": "总结关键要点和建议",
                        "word_count": 300,
                        "importance": 0.20,
                        "suggested_sources": []
                    }
                ]
            },
            "daily": {
                "title": "AI日报",
                "sections": [
                    {
                        "id": 1,
                        "title": "今日概览",
                        "requirements": "总览当日重要事件",
                        "word_count": 300,
                        "importance": 0.25,
                        "suggested_sources": []
                    },
                    {
                        "id": 2,
                        "title": "重点事件",
                        "requirements": "详述2-3个重点事件",
                        "word_count": 500,
                        "importance": 0.50,
                        "suggested_sources": []
                    },
                    {
                        "id": 3,
                        "title": "总结",
                        "requirements": "总结要点和展望",
                        "word_count": 200,
                        "importance": 0.25,
                        "suggested_sources": []
                    }
                ]
            }
        }

        return default_outlines.get(report_type, default_outlines["comprehensive"])
