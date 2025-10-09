"""
ECharts 图表生成器 - 专业数据可视化支持
基于优秀商业案例的实现
"""
import json
from typing import Dict, Any, List, Optional


class EChartsGenerator:
    """ECharts 图表配置生成器"""

    def __init__(self):
        self.charts = []

    def add_bar_chart(
        self,
        chart_id: str,
        title: str,
        categories: List[str],
        data: List[float],
        y_axis_name: str = "数值",
        color: str = "#5470c6",
        subtitle: str = ""
    ) -> Dict[str, Any]:
        """
        生成柱状图配置

        Args:
            chart_id: 图表容器ID
            title: 图表标题
            categories: X轴分类数据
            data: Y轴数值数据
            y_axis_name: Y轴名称
            color: 柱子颜色
            subtitle: 副标题
        """
        option = {
            "title": {
                "text": title,
                "subtext": subtitle,
                "left": "center",
                "textStyle": {"fontSize": 18, "fontWeight": "bold"}
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "data": categories,
                "axisLabel": {"fontSize": 14}
            },
            "yAxis": {
                "type": "value",
                "name": y_axis_name,
                "axisLabel": {"fontSize": 12}
            },
            "series": [{
                "name": y_axis_name,
                "type": "bar",
                "barWidth": "50%",
                "data": [{"value": v, "itemStyle": {"color": color}} for v in data],
                "label": {
                    "show": True,
                    "position": "top",
                    "fontSize": 14,
                    "fontWeight": "bold"
                }
            }],
            "animation": False
        }

        chart = {
            "id": chart_id,
            "title": title,
            "option": json.dumps(option, ensure_ascii=False)
        }
        self.charts.append(chart)
        return chart

    def add_line_chart(
        self,
        chart_id: str,
        title: str,
        categories: List[str],
        data: List[float],
        y_axis_name: str = "数值",
        smooth: bool = True,
        area: bool = True,
        subtitle: str = ""
    ) -> Dict[str, Any]:
        """
        生成折线图配置

        Args:
            chart_id: 图表容器ID
            title: 图表标题
            categories: X轴分类数据
            data: Y轴数值数据
            y_axis_name: Y轴名称
            smooth: 是否平滑曲线
            area: 是否显示面积
            subtitle: 副标题
        """
        series_config = {
            "name": y_axis_name,
            "type": "line",
            "data": data,
            "smooth": smooth,
            "label": {
                "show": True,
                "position": "top",
                "fontSize": 12
            },
            "markPoint": {
                "data": [
                    {"type": "max", "name": "最大值"},
                    {"type": "min", "name": "最小值"}
                ]
            }
        }

        if area:
            series_config["areaStyle"] = {}

        option = {
            "title": {
                "text": title,
                "subtext": subtitle,
                "left": "center",
                "textStyle": {"fontSize": 18, "fontWeight": "bold"}
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "boundaryGap": False,
                "data": categories,
                "axisLabel": {"fontSize": 14}
            },
            "yAxis": {
                "type": "value",
                "name": y_axis_name,
                "axisLabel": {"fontSize": 12}
            },
            "series": [series_config],
            "animation": False
        }

        chart = {
            "id": chart_id,
            "title": title,
            "option": json.dumps(option, ensure_ascii=False)
        }
        self.charts.append(chart)
        return chart

    def add_pie_chart(
        self,
        chart_id: str,
        title: str,
        data: List[Dict[str, Any]],
        subtitle: str = ""
    ) -> Dict[str, Any]:
        """
        生成饼图配置

        Args:
            chart_id: 图表容器ID
            title: 图表标题
            data: 数据列表，格式: [{"name": "分类1", "value": 100}, ...]
            subtitle: 副标题
        """
        option = {
            "title": {
                "text": title,
                "subtext": subtitle,
                "left": "center",
                "textStyle": {"fontSize": 18, "fontWeight": "bold"}
            },
            "tooltip": {
                "trigger": "item",
                "formatter": "{a} <br/>{b}: {c} ({d}%)"
            },
            "legend": {
                "orient": "vertical",
                "left": "left"
            },
            "series": [{
                "name": title,
                "type": "pie",
                "radius": "60%",
                "data": data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                },
                "label": {
                    "fontSize": 14
                }
            }],
            "animation": False
        }

        chart = {
            "id": chart_id,
            "title": title,
            "option": json.dumps(option, ensure_ascii=False)
        }
        self.charts.append(chart)
        return chart

    def add_dual_axis_chart(
        self,
        chart_id: str,
        title: str,
        categories: List[str],
        bar_data: List[float],
        line_data: List[float],
        bar_name: str = "柱状数据",
        line_name: str = "折线数据",
        bar_y_axis_name: str = "左轴",
        line_y_axis_name: str = "右轴",
        subtitle: str = ""
    ) -> Dict[str, Any]:
        """
        生成双轴图表（柱状+折线）

        Args:
            chart_id: 图表容器ID
            title: 图表标题
            categories: X轴分类数据
            bar_data: 柱状图数据
            line_data: 折线图数据
            bar_name: 柱状图名称
            line_name: 折线图名称
            bar_y_axis_name: 左Y轴名称
            line_y_axis_name: 右Y轴名称
            subtitle: 副标题
        """
        option = {
            "title": {
                "text": title,
                "subtext": subtitle,
                "left": "center",
                "textStyle": {"fontSize": 18, "fontWeight": "bold"}
            },
            "legend": {
                "data": [bar_name, line_name],
                "top": "bottom"
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "10%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "data": categories,
                "axisPointer": {"type": "shadow"},
                "axisLabel": {"interval": 0, "rotate": 30}
            },
            "yAxis": [
                {
                    "type": "value",
                    "name": bar_y_axis_name,
                    "min": 0,
                    "axisLabel": {"formatter": "{value}"}
                },
                {
                    "type": "value",
                    "name": line_y_axis_name,
                    "min": 0,
                    "axisLabel": {"formatter": "{value}"}
                }
            ],
            "series": [
                {
                    "name": bar_name,
                    "type": "bar",
                    "data": bar_data,
                    "label": {"show": True, "position": "top"}
                },
                {
                    "name": line_name,
                    "type": "line",
                    "yAxisIndex": 1,
                    "data": line_data,
                    "label": {"show": True}
                }
            ],
            "animation": False
        }

        chart = {
            "id": chart_id,
            "title": title,
            "option": json.dumps(option, ensure_ascii=False)
        }
        self.charts.append(chart)
        return chart

    def add_heatmap(
        self,
        chart_id: str,
        title: str,
        x_categories: List[str],
        y_categories: List[str],
        data: List[List[Any]],
        subtitle: str = ""
    ) -> Dict[str, Any]:
        """
        生成热力图

        Args:
            chart_id: 图表容器ID
            title: 图表标题
            x_categories: X轴分类
            y_categories: Y轴分类
            data: 数据，格式: [[x_index, y_index, value], ...]
            subtitle: 副标题
        """
        option = {
            "title": {
                "text": title,
                "subtext": subtitle,
                "left": "center",
                "textStyle": {"fontSize": 18, "fontWeight": "bold"}
            },
            "grid": {
                "height": "60%",
                "top": "15%"
            },
            "xAxis": {
                "type": "category",
                "data": x_categories,
                "splitArea": {"show": True},
                "axisLabel": {"interval": 0, "rotate": 30}
            },
            "yAxis": {
                "type": "category",
                "data": y_categories,
                "splitArea": {"show": True}
            },
            "visualMap": {
                "min": 0,
                "max": 1,
                "calculable": False,
                "orient": "horizontal",
                "left": "center",
                "bottom": "5%",
                "show": True
            },
            "series": [{
                "name": title,
                "type": "heatmap",
                "data": data,
                "label": {
                    "show": True,
                    "fontSize": 14,
                    "fontWeight": "bold"
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }],
            "animation": False
        }

        chart = {
            "id": chart_id,
            "title": title,
            "option": json.dumps(option, ensure_ascii=False)
        }
        self.charts.append(chart)
        return chart

    def add_graph_chart(
        self,
        chart_id: str,
        title: str,
        nodes: List[Dict[str, Any]],
        links: List[Dict[str, str]],
        subtitle: str = ""
    ) -> Dict[str, Any]:
        """
        生成关系图谱

        Args:
            chart_id: 图表容器ID
            title: 图表标题
            nodes: 节点列表，格式: [{"name": "节点1", "x": 100, "y": 100, "symbolSize": 80}, ...]
            links: 连接列表，格式: [{"source": "节点1", "target": "节点2"}, ...]
            subtitle: 副标题
        """
        option = {
            "title": {
                "text": title,
                "subtext": subtitle,
                "left": "center",
                "textStyle": {"fontSize": 18, "fontWeight": "bold"}
            },
            "series": [{
                "type": "graph",
                "layout": "none",
                "symbolSize": 80,
                "roam": False,
                "label": {
                    "show": True,
                    "fontSize": 12,
                    "color": "#fff",
                    "formatter": lambda params: params["name"].replace(" ", "\n")
                },
                "edgeSymbol": ["circle", "arrow"],
                "edgeSymbolSize": [4, 10],
                "data": nodes,
                "links": links,
                "animation": False
            }]
        }

        chart = {
            "id": chart_id,
            "title": title,
            "option": json.dumps(option, ensure_ascii=False)
        }
        self.charts.append(chart)
        return chart

    def get_all_charts(self) -> List[Dict[str, Any]]:
        """获取所有已创建的图表配置"""
        return self.charts

    def clear(self):
        """清空所有图表"""
        self.charts = []
