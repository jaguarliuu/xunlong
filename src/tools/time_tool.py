"""
时间工具 - 为LLM提供准确的时间信息
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import pytz
import re


class TimeTool:
    """时间工具类，提供各种时间相关功能"""

    def __init__(self):
        self.beijing_tz = pytz.timezone('Asia/Shanghai')

    def get_current_time(self) -> Dict[str, Any]:
        """获取当前时间信息"""
        now = datetime.now(self.beijing_tz)

        return {
            "current_datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "current_date": now.strftime("%Y-%m-%d"),
            "current_year": now.year,
            "current_month": now.month,
            "current_day": now.day,
            "weekday": now.strftime("%A"),
            "weekday_chinese": self._get_chinese_weekday(now.weekday()),
            "timezone": "Asia/Shanghai (UTC+8)",
            "timestamp": int(now.timestamp())
        }

    def _get_chinese_weekday(self, weekday: int) -> str:
        """获取中文星期"""
        weekdays = {
            0: "星期一",
            1: "星期二",
            2: "星期三",
            3: "星期四",
            4: "星期五",
            5: "星期六",
            6: "星期日"
        }
        return weekdays.get(weekday, "未知")

    def _create_date_entry(self, target: datetime) -> Dict[str, Any]:
        """根据datetime对象创建标准日期结构"""
        return {
            "year": target.year,
            "month": target.month,
            "day": target.day,
            "formatted": target.strftime("%Y-%m-%d")
        }

    def parse_date_query(self, query: str) -> Dict[str, Any]:
        """解析查询中的时间信息"""
        current_time = self.get_current_time()
        now = datetime.now(self.beijing_tz)

        result = {
            "current_time": current_time,
            "query_contains_date": False,
            "extracted_dates": [],
            "time_context": "",
            "time_filter": None,
            "relative_reference": None
        }

        # 匹配 YYYY年MM月DD日 / YYYY-MM-DD / YYYY/MM/DD
        date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{4})/(\d{1,2})/(\d{1,2})'
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                year, month, day = [int(x) for x in match]
                entry = self._create_date_entry(datetime(year, month, day, tzinfo=self.beijing_tz))
                result["extracted_dates"].append(entry)

        if result["extracted_dates"]:
            result["query_contains_date"] = True

        # 处理相对时间表达
        if not result["extracted_dates"]:
            lowered = query.lower()
            if any(token in lowered for token in ["今天", "今日", "当日", "本日", "today"]):
                entry = self._create_date_entry(now)
                result["extracted_dates"].append(entry)
                result["query_contains_date"] = True
                result["relative_reference"] = "today"
            elif any(token in lowered for token in ["昨天", "昨日", "上一天", "yesterday"]):
                entry = self._create_date_entry(now - timedelta(days=1))
                result["extracted_dates"].append(entry)
                result["query_contains_date"] = True
                result["relative_reference"] = "yesterday"
            elif any(token in lowered for token in ["前天", "day before yesterday"]):
                entry = self._create_date_entry(now - timedelta(days=2))
                result["extracted_dates"].append(entry)
                result["query_contains_date"] = True
                result["relative_reference"] = "day_before_yesterday"
            elif any(token in lowered for token in ["本周", "这周", "本星期", "this week"]):
                result["time_filter"] = "week"
                result["relative_reference"] = "this_week"
            elif any(token in lowered for token in ["上周", "last week"]):
                result["time_filter"] = "week"
                result["relative_reference"] = "last_week"
            elif any(token in lowered for token in ["本月", "这个月", "this month"]):
                result["time_filter"] = "month"
                result["relative_reference"] = "this_month"

        # 根据提取到的日期计算推荐时间过滤器
        if result["extracted_dates"]:
            result["time_filter"] = self._determine_time_filter(result["extracted_dates"], now)

        # 生成时间上下文提示
        if result["query_contains_date"]:
            dates_str = ", ".join([d["formatted"] for d in result["extracted_dates"]])
            filter_desc = f" 推荐检索范围: {result['time_filter']}" if result.get("time_filter") else ""
            result["time_context"] = (
                f"查询涉及具体日期: {dates_str}。当前时间: {current_time['current_datetime']}。"
                f"请确保搜索和分析的内容严格匹配指定的日期。{filter_desc}"
            )
        else:
            result["time_context"] = (
                f"当前时间: {current_time['current_datetime']}。"
                "如果查询涉及'今天'、'最近'等相对时间，请基于当前时间进行理解。"
            )

        return result

    def _determine_time_filter(self, extracted_dates: List[Dict[str, Any]], now: datetime) -> Optional[str]:
        """根据目标日期和当前时间推荐DuckDuckGo时间过滤器"""
        if not extracted_dates:
            return None

        try:
            first = extracted_dates[0]
            target = datetime(
                first["year"],
                first["month"],
                first["day"],
                tzinfo=self.beijing_tz
            )
            diff_days = abs((now.date() - target.date()).days)

            if diff_days <= 1:
                return "day"
            if diff_days <= 7:
                return "week"
            if diff_days <= 31:
                return "month"
            return None
        except Exception:
            return None

    def is_date_relevant(self, content_date: str, target_date: str, tolerance_days: int = 1) -> bool:
        """判断内容日期是否与目标日期相关"""
        try:
            content_dt = datetime.strptime(content_date, "%Y-%m-%d")
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")

            diff = abs((content_dt - target_dt).days)
            return diff <= tolerance_days

        except Exception:
            return False

    def format_time_for_search(self, date_info: Dict[str, Any]) -> str:
        """为搜索查询格式化时间信息"""
        if not date_info.get("extracted_dates"):
            return ""

        date = date_info["extracted_dates"][0]
        return f"{date['year']}年{date['month']}月{date['day']}日"


# 全局时间工具实例
time_tool = TimeTool()
