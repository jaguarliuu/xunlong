"""
段落写作智能体 - 撰写报告的特定段落
"""
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager


class SectionWriter:
    """段落写作智能体"""

    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = "段落写作者"

    async def write_section(
        self,
        section: Dict[str, Any],
        available_content: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """撰写单个段落"""

        section_id = section.get("id")
        section_title = section.get("title")

        logger.info(f"[{self.name}] 开始撰写段落 {section_id}: {section_title}")

        try:
            # 筛选相关内容
            relevant_content = self._filter_relevant_content(
                section, available_content
            )

            # 暂时关闭图片插入，保留逻辑以便后续启用
            section_images = []

            # 构建写作提示
            writing_prompt = self._build_writing_prompt(
                section, relevant_content, context
            )

            # 调用LLM撰写
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                writing_prompt,
                "你是一个专业的内容撰写专家，擅长撰写结构清晰、逻辑严谨的报告段落。"
            )

            # 暂时不进行图片插入
            enhanced_content = response

            # 计算置信度
            confidence = self._calculate_confidence(
                enhanced_content, section, relevant_content
            )

            # 识别问题
            issues = self._identify_issues(enhanced_content, section)

            result = {
                "section_id": section_id,
                "title": section_title,
                "content": enhanced_content,
                "confidence": confidence,
                "sources_used": [c.get("url", "") for c in relevant_content[:5]],
                "word_count": len(enhanced_content),
                "issues": issues,
                "status": "success",
                "images": section_images,
                "image_count": len(section_images),
                "images_inserted": bool(section_images)
            }

            logger.info(
                f"[{self.name}] 段落 {section_id} 完成，"
                f"字数: {len(enhanced_content)}, "
                f"置信度: {confidence:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"[{self.name}] 段落 {section_id} 撰写失败: {e}")
            return {
                "section_id": section_id,
                "title": section_title,
                "content": "",
                "confidence": 0.0,
                "sources_used": [],
                "word_count": 0,
                "issues": [f"撰写失败: {str(e)}"],
                "status": "error",
                "error": str(e),
                "images": [],
                "image_count": 0,
                "images_inserted": False
            }

    async def rewrite_section(
        self,
        section_result: Dict[str, Any],
        suggestions: List[str],
        additional_content: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """重写段落"""

        section_id = section_result.get("section_id")
        logger.info(f"[{self.name}] 重写段落 {section_id}")

        try:
            # 构建重写提示
            rewrite_prompt = self._build_rewrite_prompt(
                section_result, suggestions, additional_content
            )

            # 调用LLM重写
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                rewrite_prompt,
                "你是一个专业的内容修改专家，擅长根据反馈改进文本质量。"
            )

            # 更新结果
            section_result["content"] = response
            section_result["word_count"] = len(response)
            section_result["confidence"] = self._calculate_confidence(
                response, {"requirements": section_result.get("title", "")}, []
            )

            logger.info(f"[{self.name}] 段落 {section_id} 重写完成")

            return section_result

        except Exception as e:
            logger.error(f"[{self.name}] 段落 {section_id} 重写失败: {e}")
            section_result["issues"].append(f"重写失败: {str(e)}")
            return section_result

    def _filter_relevant_content(
        self,
        section: Dict[str, Any],
        available_content: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """筛选与段落相关的内容"""

        section_title = section.get("title", "").lower()
        requirements = section.get("requirements", "").lower()
        suggested_sources = section.get("suggested_sources", [])

        relevant = []

        for content in available_content:
            score = 0

            # 标题匹配
            title = content.get("title", "").lower()
            if any(word in title for word in section_title.split()):
                score += 2

            # 内容匹配
            text = content.get("content", "").lower()
            if any(word in text for word in requirements.split()):
                score += 1

            # 建议来源匹配
            if title in [s.lower() for s in suggested_sources]:
                score += 3

            if score > 0:
                relevant.append((score, content))

        # 按分数排序
        relevant.sort(key=lambda x: x[0], reverse=True)

        return [content for score, content in relevant[:10]]

    def _build_writing_prompt(
        self,
        section: Dict[str, Any],
        relevant_content: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """构建写作提示"""

        section_id = section.get("id")
        title = section.get("title")
        requirements = section.get("requirements")
        word_count = section.get("word_count", 500)

        # 准备参考内容
        references = self._format_references(relevant_content)

        # 获取上下文
        query = context.get("query", "") if context else ""
        report_type = context.get("report_type", "comprehensive") if context else "comprehensive"
        previous_section = context.get("previous_section", "") if context else ""

        prompt = f"""# 段落撰写任务

## 段落信息
- 段落编号: {section_id}
- 段落标题: {title}
- 目标字数: {word_count} 字

## 写作要求
{requirements}

## 查询背景
{query}

## 报告类型
{report_type}

{"## 上一段内容（保持连贯）" if previous_section else ""}
{previous_section[:200] + "..." if previous_section else ""}

## 参考内容
以下是可用的信息来源，请基于这些内容撰写：

{references}

## 撰写指南

1. **内容要求**:
   - 严格按照"写作要求"撰写
   - 使用参考内容中的事实和数据
   - 保持客观、准确、专业
   - 逻辑清晰，结构合理

2. **格式要求**:
   - 使用Markdown格式
   - 适当使用标题、列表、加粗等
   - 字数控制在 {word_count} ± 20% 之间

3. **质量要求**:
   - 确保信息完整性
   - 避免重复和冗余
   - 引用数据时注明来源
   - 保持与上下文的连贯性

4. **禁止事项**:
   - 不要杜撰不存在的数据
   - 不要超出参考内容范围
   - 不要添加个人观点（除非报告类型要求）

## 输出要求

请直接输出段落内容，不要添加额外说明。内容应：
- 紧扣主题
- 信息丰富
- 逻辑严密
- 易于阅读

开始撰写：
"""

        return prompt

    def _collect_section_images(
        self,
        relevant_content: List[Dict[str, Any]],
        section_title: Optional[str] = None,
        max_images: int = 4
    ) -> List[Dict[str, Any]]:
        """从相关内容中收集图片用于插入段落"""

        collected: List[Dict[str, Any]] = []
        seen_keys = set()

        for content in relevant_content:
            images = content.get("images") or []
            if not images:
                continue

            for img in images:
                if not isinstance(img, dict):
                    continue

                key = img.get("url") or img.get("local_path")
                if not key or key in seen_keys:
                    continue

                seen_keys.add(key)

                alt_text = img.get("alt") or content.get("title") or section_title or "相关图片"
                sanitized = {
                    "url": img.get("url"),
                    "local_path": "",  # 使用远程链接，避免路径不一致
                    "alt": alt_text,
                    "width": img.get("width"),
                    "height": img.get("height"),
                    "source": content.get("title") or content.get("url"),
                    "source_title": content.get("title", ""),
                    "source_url": content.get("url", ""),
                    "search_query": content.get("search_query"),
                    "original_local_path": img.get("local_path")
                }

                collected.append(sanitized)

                if len(collected) >= max_images:
                    return collected

        return collected

    def _format_references(self, content_list: List[Dict[str, Any]]) -> str:
        """格式化参考内容"""

        if not content_list:
            return "暂无参考内容，请基于查询背景进行撰写。"

        formatted = []
        for i, content in enumerate(content_list[:8], 1):
            title = content.get("title", "无标题")
            url = content.get("url", "")
            text = content.get("content", "")[:500]

            formatted.append(f"""
### 来源 {i}: {title}
**URL**: {url}
**内容摘要**: {text}...
""")

        return "\n".join(formatted)

    def _calculate_confidence(
        self,
        content: str,
        section: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> float:
        """计算撰写置信度"""

        confidence = 0.5  # 基础分

        # 长度检查
        word_count = len(content)
        target_count = section.get("word_count", 500)

        if 0.8 * target_count <= word_count <= 1.2 * target_count:
            confidence += 0.2
        elif 0.6 * target_count <= word_count <= 1.4 * target_count:
            confidence += 0.1

        # 结构检查（是否使用Markdown）
        if "#" in content or "**" in content or "-" in content:
            confidence += 0.1

        # 信息来源检查
        if sources:
            confidence += min(0.2, len(sources) * 0.05)

        return min(1.0, confidence)

    def _identify_issues(
        self,
        content: str,
        section: Dict[str, Any]
    ) -> List[str]:
        """识别潜在问题"""

        issues = []

        # 长度检查
        word_count = len(content)
        target_count = section.get("word_count", 500)

        if word_count < 0.6 * target_count:
            issues.append(f"内容过短 ({word_count} 字 < 目标 {target_count} 字)")

        if word_count > 1.4 * target_count:
            issues.append(f"内容过长 ({word_count} 字 > 目标 {target_count} 字)")

        # 空洞检查
        if content.count("。") < 3:
            issues.append("内容可能过于简单")

        # 格式检查
        if not any(marker in content for marker in ["#", "**", "-", "•"]):
            issues.append("缺少格式化元素")

        return issues

    def _build_rewrite_prompt(
        self,
        section_result: Dict[str, Any],
        suggestions: List[str],
        additional_content: Optional[List[Dict[str, Any]]]
    ) -> str:
        """构建重写提示"""

        original_content = section_result.get("content", "")
        section_title = section_result.get("title", "")

        additional_refs = ""
        if additional_content:
            additional_refs = self._format_references(additional_content)

        prompt = f"""# 段落重写任务

## 原始段落
### {section_title}
{original_content}

## 改进建议
{chr(10).join(f"- {s}" for s in suggestions)}

{"## 补充参考内容" if additional_refs else ""}
{additional_refs}

## 重写要求

请根据改进建议重写本段落，确保：

1. **解决所有指出的问题**
2. **保留原有的正确内容**
3. **整合补充的参考内容**（如有）
4. **提升整体质量和连贯性**

请直接输出重写后的内容：
"""

        return prompt
