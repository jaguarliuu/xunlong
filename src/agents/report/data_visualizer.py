"""
数据可视化智能体

从文本内容中识别数据，生成表格和图表
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import json
import re

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager
from ..base import BaseAgent, AgentConfig


class DataVisualizer(BaseAgent):
    """数据可视化智能体 - 识别数据并生成表格和图表"""

    def __init__(
        self,
        llm_manager: LLMManager,
        prompt_manager: PromptManager = None
    ):
        config = AgentConfig(
            name="数据可视化智能体",
            description="从文本中识别数据，生成表格和可视化图表",
            llm_config_name="data_visualizer",
            temperature=0.3,  # 数据处理需要更精确
            max_tokens=3000
        )
        super().__init__(llm_manager, prompt_manager, config)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理内容，识别数据并生成可视化

        Args:
            input_data: {
                "content": "原始文本内容",
                "title": "章节标题（可选）"
            }

        Returns:
            {
                "status": "success/error",
                "enhanced_content": "增强后的内容（包含表格和图表）",
                "visualizations": [
                    {
                        "type": "table/chart",
                        "title": "可视化标题",
                        "data": {...},
                        "markdown": "Markdown格式",
                        "html": "HTML格式"
                    }
                ]
            }
        """
        try:
            content = input_data.get("content", "")
            title = input_data.get("title", "")

            if not content:
                return {
                    "status": "error",
                    "message": "内容为空",
                    "enhanced_content": content,
                    "visualizations": []
                }

            logger.info(f"[{self.name}] 分析内容，识别数据...")

            # 使用LLM识别数据并生成可视化
            system_prompt = self._get_system_prompt()
            user_prompt = self._build_user_prompt(content, title)

            response = await self.get_llm_response(user_prompt, system_prompt)

            # 解析LLM返回的数据可视化建议
            viz_result = self._parse_visualization_response(response)

            if not viz_result["visualizations"]:
                logger.info(f"[{self.name}] 未识别到需要可视化的数据")
                return {
                    "status": "success",
                    "enhanced_content": content,
                    "visualizations": []
                }

            # 生成表格和图表
            visualizations = []
            for viz in viz_result["visualizations"]:
                generated_viz = await self._generate_visualization(viz)
                if generated_viz:
                    visualizations.append(generated_viz)

            logger.info(
                f"[{self.name}] 成功生成 {len(visualizations)} 个可视化 "
                f"({sum(1 for v in visualizations if v['type'] == 'table')} 个表格, "
                f"{sum(1 for v in visualizations if v['type'] == 'chart')} 个图表)"
            )

            # 对于HTML，可视化会单独渲染，不插入到content
            # 对于Markdown，可以选择插入
            return {
                "status": "success",
                "enhanced_content": content,  # 保持原始内容
                "visualizations": visualizations
            }

        except Exception as e:
            logger.error(f"[{self.name}] 数据可视化失败: {e}")
            return {
                "status": "error",
                "message": str(e),
                "enhanced_content": input_data.get("content", ""),
                "visualizations": []
            }

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个数据可视化专家，擅长从文本中识别数据并生成表格和图表。

你的任务：
1. 分析文本内容，识别可以可视化的数据
2. 判断使用表格还是图表更合适
3. 提取数据并结构化
4. 提供可视化建议

数据类型判断：
- 对比数据（A vs B）→ 表格或柱状图
- 趋势数据（时间序列）→ 折线图或表格
- 占比数据（百分比）→ 饼图或表格
- 排名数据（Top N）→ 表格或条形图
- 多维数据 → 表格

输出格式（JSON）：
{
  "visualizations": [
    {
      "type": "table/bar/line/pie",
      "title": "可视化标题",
      "data": {
        // 根据type不同，数据格式不同
      },
      "position": "after_paragraph_X"  // 插入位置提示
    }
  ]
}

注意：
- 只识别明确的数据，不要臆造
- 如果没有合适的数据，返回空数组
- 优先使用表格，图表作为补充
"""

    def _build_user_prompt(self, content: str, title: str = "") -> str:
        """构建用户提示词"""
        prompt = f"""请分析以下内容，识别可以可视化的数据：

"""
        if title:
            prompt += f"章节标题：{title}\n\n"

        prompt += f"""内容：
{content}

请以JSON格式返回可视化建议，如果没有合适的数据，返回空的visualizations数组。"""

        return prompt

    def _parse_visualization_response(self, response: str) -> Dict[str, Any]:
        """解析LLM返回的可视化建议"""
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group(0))
                return result
            else:
                return {"visualizations": []}
        except Exception as e:
            logger.error(f"解析可视化建议失败: {e}")
            return {"visualizations": []}

    async def _generate_visualization(
        self,
        viz_spec: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """生成具体的可视化（表格或图表）"""
        try:
            viz_type = viz_spec.get("type", "table")
            title = viz_spec.get("title", "数据可视化")
            data = viz_spec.get("data", {})

            if viz_type == "table":
                return self._generate_table(title, data)
            elif viz_type in ["bar", "line", "pie"]:
                return self._generate_chart(viz_type, title, data)
            else:
                logger.warning(f"不支持的可视化类型: {viz_type}")
                return None

        except Exception as e:
            logger.error(f"生成可视化失败: {e}")
            return None

    def _generate_table(
        self,
        title: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成表格"""
        headers = data.get("headers", [])
        rows = data.get("rows", [])

        if not headers or not rows:
            return None

        # 生成Markdown表格
        md_lines = [f"**{title}**\n"]
        md_lines.append("| " + " | ".join(headers) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        for row in rows:
            md_lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

        markdown = "\n".join(md_lines)

        # 生成HTML表格
        html_lines = [f'<div class="data-table">']
        html_lines.append(f'<h4>{title}</h4>')
        html_lines.append('<table>')
        html_lines.append('<thead><tr>')
        for header in headers:
            html_lines.append(f'<th>{header}</th>')
        html_lines.append('</tr></thead>')
        html_lines.append('<tbody>')

        for row in rows:
            html_lines.append('<tr>')
            for cell in row:
                html_lines.append(f'<td>{cell}</td>')
            html_lines.append('</tr>')

        html_lines.append('</tbody></table></div>')

        html = "\n".join(html_lines)

        return {
            "type": "table",
            "title": title,
            "data": data,
            "markdown": markdown,
            "html": html
        }

    def _generate_chart(
        self,
        chart_type: str,
        title: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成图表（使用ECharts）"""
        import uuid
        chart_id = f"chart_{uuid.uuid4().hex[:8]}"

        # 根据图表类型构建ECharts配置
        echarts_option = self._build_echarts_option(chart_type, title, data)

        if not echarts_option:
            return None

        # 生成Markdown（描述）
        markdown = f"**{title}** [图表]\n\n> 此处将显示{self._get_chart_type_name(chart_type)}"

        # 生成HTML（ECharts）- 使用DOMContentLoaded确保在页面加载后执行
        html = f'''<div class="data-chart">
<div id="{chart_id}" style="width: 100%; height: 400px;"></div>
<script>
(function() {{
  function initChart() {{
    if (typeof echarts === 'undefined') {{
      console.error('ECharts library not loaded for {chart_id}');
      return;
    }}
    var chartDom = document.getElementById('{chart_id}');
    if (!chartDom) {{
      console.error('Chart container not found: {chart_id}');
      return;
    }}
    var chart = echarts.init(chartDom);
    var option = {json.dumps(echarts_option, ensure_ascii=False)};
    chart.setOption(option);
    window.addEventListener('resize', function() {{
      chart.resize();
    }});
  }}

  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', initChart);
  }} else {{
    initChart();
  }}
}})();
</script>
</div>'''

        return {
            "type": "chart",
            "chart_type": chart_type,
            "title": title,
            "data": data,
            "markdown": markdown,
            "html": html,
            "chart_id": chart_id
        }

    def _build_echarts_option(
        self,
        chart_type: str,
        title: str,
        data: Dict[str, Any]
    ) -> Optional[Dict]:
        """构建ECharts配置"""
        try:
            if chart_type == "bar":
                return {
                    "title": {"text": title},
                    "tooltip": {},
                    "xAxis": {"type": "category", "data": data.get("labels", [])},
                    "yAxis": {"type": "value"},
                    "series": [{
                        "type": "bar",
                        "data": data.get("values", [])
                    }]
                }
            elif chart_type == "line":
                return {
                    "title": {"text": title},
                    "tooltip": {},
                    "xAxis": {"type": "category", "data": data.get("labels", [])},
                    "yAxis": {"type": "value"},
                    "series": [{
                        "type": "line",
                        "data": data.get("values", [])
                    }]
                }
            elif chart_type == "pie":
                pie_data = [
                    {"name": label, "value": value}
                    for label, value in zip(
                        data.get("labels", []),
                        data.get("values", [])
                    )
                ]
                return {
                    "title": {"text": title},
                    "tooltip": {},
                    "series": [{
                        "type": "pie",
                        "radius": "50%",
                        "data": pie_data
                    }]
                }
            else:
                return None
        except Exception as e:
            logger.error(f"构建ECharts配置失败: {e}")
            return None

    def _get_chart_type_name(self, chart_type: str) -> str:
        """获取图表类型中文名"""
        names = {
            "bar": "柱状图",
            "line": "折线图",
            "pie": "饼图"
        }
        return names.get(chart_type, "图表")

    def _insert_visualizations(
        self,
        content: str,
        visualizations: List[Dict[str, Any]]
    ) -> str:
        """将可视化插入到内容中"""
        if not visualizations:
            return content

        # 简单策略：将所有可视化添加到内容末尾
        enhanced_content = content + "\n\n"

        for viz in visualizations:
            # 使用Markdown格式（HTML生成时会自动处理）
            enhanced_content += "\n\n" + viz["markdown"] + "\n\n"

        return enhanced_content
