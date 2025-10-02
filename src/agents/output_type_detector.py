"""
输出类型检测器 - 识别用户需求的输出类型（报告/小说/PPT等）
"""
import re
from typing import Dict, Any, Optional
from loguru import logger

from ..llm.manager import LLMManager
from ..llm.prompts import PromptManager


class OutputTypeDetector:
    """输出类型检测器"""

    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = "输出类型检测器"

    async def detect_output_type(self, query: str) -> Dict[str, Any]:
        """检测查询的输出类型"""

        logger.info(f"[{self.name}] 开始检测输出类型")

        # 先尝试基于规则的快速检测
        rule_based = self._rule_based_detection(query)
        if rule_based["confidence"] > 0.8:
            logger.info(
                f"[{self.name}] 规则检测成功: {rule_based['output_type']} "
                f"(置信度: {rule_based['confidence']:.2f})"
            )
            return rule_based

        # 规则检测不确定，使用LLM辅助判断
        logger.info(f"[{self.name}] 规则检测不确定，使用LLM辅助判断")
        llm_result = await self._llm_based_detection(query)

        return llm_result

    def _rule_based_detection(self, query: str) -> Dict[str, Any]:
        """基于规则的检测"""

        query_lower = query.lower()

        # 小说创作关键词
        fiction_keywords = [
            "小说", "故事", "剧本", "写一篇", "创作", "编写",
            "fiction", "story", "novel", "narrative",
            "章节", "情节", "角色", "主角", "人物设定"
        ]

        # 报告关键词
        report_keywords = [
            "报告", "分析", "总结", "综述", "研究",
            "report", "analysis", "summary", "review",
            "日报", "调研", "评估", "整理资料"
        ]

        # PPT关键词
        ppt_keywords = [
            "ppt", "幻灯片", "演示文稿", "slide", "presentation",
            "演讲稿", "展示"
        ]

        # 计算匹配分数
        fiction_score = sum(1 for kw in fiction_keywords if kw in query_lower)
        report_score = sum(1 for kw in report_keywords if kw in query_lower)
        ppt_score = sum(1 for kw in ppt_keywords if kw in query_lower)

        # 特殊模式检测
        # 1. "写一篇XX小说" 模式
        if re.search(r'写.*?小说|创作.*?小说|编.*?故事', query):
            fiction_score += 5

        # 2. "XX日报" 模式
        if re.search(r'\d+.*?日报|每日.*?报告', query):
            report_score += 5

        # 3. "制作PPT" 模式
        if re.search(r'制作.*?ppt|做.*?幻灯片', query_lower):
            ppt_score += 5

        # 判断输出类型
        max_score = max(fiction_score, report_score, ppt_score)

        if max_score == 0:
            # 没有明确关键词，默认为报告
            return {
                "output_type": "report",
                "confidence": 0.5,
                "reason": "无明确关键词，默认为报告类型",
                "detection_method": "rule_based"
            }

        # 计算置信度
        total_score = fiction_score + report_score + ppt_score
        confidence = max_score / total_score if total_score > 0 else 0.5

        if fiction_score == max_score:
            output_type = "fiction"
            reason = f"检测到小说创作关键词 (分数: {fiction_score})"
        elif ppt_score == max_score:
            output_type = "ppt"
            reason = f"检测到PPT制作关键词 (分数: {ppt_score})"
        else:
            output_type = "report"
            reason = f"检测到报告类关键词 (分数: {report_score})"

        return {
            "output_type": output_type,
            "confidence": min(confidence, 0.95),  # 规则检测最高0.95
            "reason": reason,
            "detection_method": "rule_based",
            "scores": {
                "fiction": fiction_score,
                "report": report_score,
                "ppt": ppt_score
            }
        }

    async def _llm_based_detection(self, query: str) -> Dict[str, Any]:
        """基于LLM的检测"""

        prompt = f"""# 输出类型识别任务

请分析以下用户查询，判断用户期望的输出类型。

## 用户查询
{query}

## 输出类型定义

1. **report** (报告)
   - 用户希望获得信息整理、分析总结类的报告
   - 关键词：报告、分析、总结、日报、调研、研究
   - 示例：
     - "生成AI日报"
     - "分析人工智能发展趋势"
     - "总结区块链技术应用"

2. **fiction** (虚构创作/小说)
   - 用户希望创作小说、故事等虚构作品
   - 关键词：小说、故事、剧本、创作、编写
   - 示例：
     - "写一篇科幻小说"
     - "创作一个悬疑故事"
     - "搜集资料写推理小说"

3. **ppt** (演示文稿)
   - 用户希望生成演示文稿、幻灯片
   - 关键词：PPT、幻灯片、演示文稿
   - 示例：
     - "制作产品介绍PPT"
     - "生成项目汇报幻灯片"

## 判断要点

- **关键词匹配**：查询中是否包含特定关键词
- **动作意图**：用户希望"获取信息"还是"创作内容"
- **输出形式**：期望的最终产出是什么

## 输出格式

请严格按照以下JSON格式输出：

```json
{{
  "output_type": "report" | "fiction" | "ppt",
  "confidence": 0.95,
  "reason": "判断理由说明"
}}
```

注意：
- output_type 必须是 "report"、"fiction"、"ppt" 之一
- confidence 是置信度（0.0-1.0）
- reason 简要说明判断理由

请开始分析：
"""

        try:
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                prompt,
                "你是一个专业的需求分析专家，擅长理解用户意图。"
            )

            # 解析响应
            import json
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())

                # 验证字段
                if "output_type" in result and result["output_type"] in ["report", "fiction", "ppt"]:
                    result["detection_method"] = "llm_based"
                    logger.info(
                        f"[{self.name}] LLM检测成功: {result['output_type']} "
                        f"(置信度: {result.get('confidence', 0.8):.2f})"
                    )
                    return result

            # 解析失败，返回默认
            logger.warning(f"[{self.name}] LLM检测失败，使用默认类型")
            return {
                "output_type": "report",
                "confidence": 0.6,
                "reason": "LLM解析失败，默认为报告类型",
                "detection_method": "fallback"
            }

        except Exception as e:
            logger.error(f"[{self.name}] LLM检测出错: {e}")
            return {
                "output_type": "report",
                "confidence": 0.5,
                "reason": f"检测出错: {str(e)}，默认为报告类型",
                "detection_method": "error_fallback"
            }

    def extract_fiction_requirements(self, query: str) -> Dict[str, Any]:
        """提取小说创作的具体要求"""

        requirements = {
            "genre": None,      # 类型
            "length": None,     # 篇幅
            "theme": None,      # 主题
            "style": None,      # 风格
            "constraints": []   # 其他约束
        }

        query_lower = query.lower()

        # 提取类型
        genre_patterns = {
            "推理": ["推理", "侦探", "悬疑", "mystery", "detective"],
            "科幻": ["科幻", "sci-fi", "未来"],
            "奇幻": ["奇幻", "魔法", "fantasy"],
            "爱情": ["爱情", "言情", "romance"],
            "恐怖": ["恐怖", "惊悚", "horror"],
            "武侠": ["武侠", "仙侠", "修真"]
        }

        for genre, keywords in genre_patterns.items():
            if any(kw in query_lower for kw in keywords):
                requirements["genre"] = genre
                break

        # 提取篇幅
        if "短篇" in query or "short" in query_lower:
            requirements["length"] = "short"  # 5000字以内
        elif "中篇" in query or "medium" in query_lower:
            requirements["length"] = "medium"  # 5000-30000字
        elif "长篇" in query or "long" in query_lower:
            requirements["length"] = "long"  # 30000字以上
        else:
            requirements["length"] = "short"  # 默认短篇

        # 提取特殊约束
        special_patterns = [
            ("暴风雪山庄", "封闭空间推理"),
            ("本格", "本格推理规则"),
            ("孤岛", "孤岛模式"),
            ("密室", "密室推理"),
            ("time loop", "时间循环"),
            ("第一人称", "第一人称视角"),
            ("第三人称", "第三人称视角")
        ]

        for pattern, constraint in special_patterns:
            if pattern in query_lower:
                requirements["constraints"].append(constraint)

        return requirements
