"""
段落评估智能体 - 评估段落质量并提供改进建议
"""
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
import json
import re

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager


class SectionEvaluator:
    """段落评估智能体"""

    def __init__(
        self,
        llm_manager: LLMManager,
        prompt_manager: PromptManager,
        confidence_threshold: float = 0.7
    ):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.confidence_threshold = confidence_threshold
        self.name = "段落评估者"

    async def evaluate_section(
        self,
        section_result: Dict[str, Any],
        section_requirements: Dict[str, Any],
        available_sources: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """评估段落质量"""

        section_id = section_result.get("section_id")
        logger.info(f"[{self.name}] 开始评估段落 {section_id}")

        try:
            # 构建评估提示
            evaluation_prompt = self._build_evaluation_prompt(
                section_result, section_requirements, available_sources
            )

            # 调用LLM评估
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                evaluation_prompt,
                "你是一个专业的内容质量评估专家，擅长客观评估文本质量并提供建设性建议。"
            )

            # 解析评估结果
            evaluation = self._parse_evaluation_response(response)

            # 计算综合置信度
            confidence = self._calculate_overall_confidence(evaluation)

            # 判断是否通过
            passed = confidence >= self.confidence_threshold

            # 生成建议
            recommendation = self._generate_recommendation(
                evaluation, confidence, passed
            )

            result = {
                "section_id": section_id,
                "passed": passed,
                "confidence": confidence,
                "scores": evaluation.get("scores", {}),
                "issues": evaluation.get("issues", []),
                "recommendation": recommendation,
                "status": "success"
            }

            logger.info(
                f"[{self.name}] 段落 {section_id} 评估完成，"
                f"置信度: {confidence:.2f}, 通过: {passed}"
            )

            return result

        except Exception as e:
            logger.error(f"[{self.name}] 段落 {section_id} 评估失败: {e}")
            return {
                "section_id": section_id,
                "passed": False,
                "confidence": 0.0,
                "scores": {},
                "issues": [f"评估失败: {str(e)}"],
                "recommendation": {
                    "action": "need_rewrite",
                    "reason": "评估过程出错",
                    "suggestions": ["请检查段落内容"]
                },
                "status": "error",
                "error": str(e)
            }

    def _build_evaluation_prompt(
        self,
        section_result: Dict[str, Any],
        section_requirements: Dict[str, Any],
        available_sources: Optional[List[Dict[str, Any]]]
    ) -> str:
        """构建评估提示"""

        section_id = section_result.get("section_id")
        title = section_result.get("title")
        content = section_result.get("content")
        requirements = section_requirements.get("requirements", "")
        target_word_count = section_requirements.get("word_count", 500)

        sources_summary = ""
        if available_sources:
            sources_summary = "\n".join([
                f"- {s.get('title', '未知来源')}"
                for s in available_sources[:5]
            ])

        prompt = f"""# 段落质量评估任务

## 段落信息
- 段落编号: {section_id}
- 段落标题: {title}
- 目标字数: {target_word_count}
- 实际字数: {len(content)}

## 撰写要求
{requirements}

## 段落内容
{content}

## 可用信息源
{sources_summary if sources_summary else "暂无"}

## 评估标准

请从以下四个维度评估段落质量（每项 0-10 分）：

### 1. 完整性 (Completeness)
- 是否涵盖了撰写要求中的所有要点？
- 信息是否充分、详细？
- 是否有明显遗漏的内容？

### 2. 准确性 (Accuracy)
- 信息是否准确、可靠？
- 是否有事实错误或不准确的表述？
- 引用的数据是否正确？

### 3. 相关性 (Relevance)
- 内容是否紧扣主题？
- 是否有偏离主题的内容？
- 是否与撰写要求一致？

### 4. 连贯性 (Coherence)
- 逻辑是否清晰？
- 段落结构是否合理？
- 语言是否流畅、易读？

## 输出格式

请严格按照以下JSON格式输出评估结果：

```json
{{
  "scores": {{
    "completeness": 8.0,
    "accuracy": 9.0,
    "relevance": 8.5,
    "coherence": 7.5
  }},
  "issues": [
    "具体问题描述1",
    "具体问题描述2"
  ],
  "strengths": [
    "优点1",
    "优点2"
  ],
  "missing_info": [
    "缺少的信息1",
    "缺少的信息2"
  ],
  "suggestions": [
    "改进建议1",
    "改进建议2"
  ]
}}
```

## 评分指南

- **9-10分**: 优秀，几乎完美
- **7-8分**: 良好，有小问题
- **5-6分**: 一般，需要改进
- **3-4分**: 较差，有明显问题
- **0-2分**: 很差，需要重写

请客观、专业地评估，提供具体、可操作的建议。
"""

        return prompt

    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """解析评估响应"""

        try:
            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                evaluation = json.loads(json_str)

                # 验证必要字段
                if "scores" in evaluation:
                    return evaluation

            logger.warning(f"[{self.name}] JSON解析失败，使用默认评估")
            return self._get_fallback_evaluation()

        except Exception as e:
            logger.error(f"[{self.name}] 解析评估响应失败: {e}")
            return self._get_fallback_evaluation()

    def _get_fallback_evaluation(self) -> Dict[str, Any]:
        """获取备用评估结果"""
        return {
            "scores": {
                "completeness": 6.0,
                "accuracy": 6.0,
                "relevance": 6.0,
                "coherence": 6.0
            },
            "issues": ["评估失败，使用默认分数"],
            "strengths": [],
            "missing_info": [],
            "suggestions": ["请人工检查内容质量"]
        }

    def _calculate_overall_confidence(self, evaluation: Dict[str, Any]) -> float:
        """计算综合置信度"""

        scores = evaluation.get("scores", {})

        # 权重分配
        weights = {
            "completeness": 0.30,
            "accuracy": 0.30,
            "relevance": 0.25,
            "coherence": 0.15
        }

        # 计算加权平均（0-10 → 0-1）
        total_score = 0.0
        total_weight = 0.0

        for criterion, weight in weights.items():
            if criterion in scores:
                score = scores[criterion] / 10.0  # 归一化到 0-1
                total_score += score * weight
                total_weight += weight

        if total_weight > 0:
            confidence = total_score / total_weight
        else:
            confidence = 0.5

        return round(confidence, 2)

    def _generate_recommendation(
        self,
        evaluation: Dict[str, Any],
        confidence: float,
        passed: bool
    ) -> Dict[str, Any]:
        """生成改进建议"""

        if passed:
            return {
                "action": "approve",
                "reason": f"质量良好，置信度 {confidence:.2f} 达到阈值",
                "suggestions": []
            }

        scores = evaluation.get("scores", {})
        issues = evaluation.get("issues", [])
        missing_info = evaluation.get("missing_info", [])
        suggestions = evaluation.get("suggestions", [])

        # 判断问题类型
        avg_score = sum(scores.values()) / len(scores) if scores else 5.0

        # 如果主要是信息缺失问题
        if missing_info and scores.get("completeness", 10) < 7:
            return {
                "action": "need_more_content",
                "reason": "信息不完整，需要补充内容",
                "missing_info": missing_info,
                "suggestions": suggestions
            }

        # 如果主要是质量问题
        if avg_score < 6:
            return {
                "action": "need_rewrite",
                "reason": "整体质量不足，需要重写",
                "issues": issues,
                "suggestions": suggestions
            }

        # 其他情况，建议修改
        return {
            "action": "need_rewrite",
            "reason": f"置信度 {confidence:.2f} 未达到阈值 {self.confidence_threshold}",
            "issues": issues,
            "suggestions": suggestions
        }

    async def batch_evaluate(
        self,
        section_results: List[Dict[str, Any]],
        section_requirements: List[Dict[str, Any]],
        available_sources: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """批量评估多个段落"""

        logger.info(f"[{self.name}] 开始批量评估 {len(section_results)} 个段落")

        # 创建评估任务
        tasks = []
        for section_result in section_results:
            section_id = section_result.get("section_id")
            # 找到对应的要求
            requirements = next(
                (r for r in section_requirements if r.get("id") == section_id),
                {}
            )
            task = self.evaluate_section(section_result, requirements, available_sources)
            tasks.append(task)

        # 并行评估
        evaluations = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        results = []
        for i, evaluation in enumerate(evaluations):
            if isinstance(evaluation, Exception):
                logger.error(f"[{self.name}] 段落 {i+1} 评估出错: {evaluation}")
                results.append({
                    "section_id": i + 1,
                    "passed": False,
                    "confidence": 0.0,
                    "status": "error",
                    "error": str(evaluation)
                })
            else:
                results.append(evaluation)

        passed_count = sum(1 for r in results if r.get("passed"))
        logger.info(f"[{self.name}] 批量评估完成，{passed_count}/{len(results)} 个段落通过")

        return results
