"""
时间工具 - 为LLM提供准确的时间信息
"""
from datetime import datetime, timezone
from typing import Dict, Any
import pytz

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
    
    def parse_date_query(self, query: str) -> Dict[str, Any]:
        """解析查询中的时间信息"""
        current_time = self.get_current_time()
        
        # 基本的时间解析逻辑
        result = {
            "current_time": current_time,
            "query_contains_date": False,
            "extracted_dates": [],
            "time_context": ""
        }
        
        # 检查是否包含具体日期
        import re
        
        # 匹配 YYYY年MM月DD日 或 YYYY-MM-DD 格式
        date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{4})/(\d{1,2})/(\d{1,2})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, query)
            if matches:
                result["query_contains_date"] = True
                for match in matches:
                    year, month, day = match
                    result["extracted_dates"].append({
                        "year": int(year),
                        "month": int(month),
                        "day": int(day),
                        "formatted": f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    })
        
        # 生成时间上下文提示
        if result["query_contains_date"]:
            dates_str = ", ".join([d["formatted"] for d in result["extracted_dates"]])
            result["time_context"] = f"查询涉及具体日期: {dates_str}。当前时间: {current_time['current_datetime']}。请确保搜索和分析的内容严格匹配指定的日期。"
        else:
            result["time_context"] = f"当前时间: {current_time['current_datetime']}。如果查询涉及'今天'、'最近'等相对时间，请基于当前时间进行理解。"
        
        return result
    
    def is_date_relevant(self, content_date: str, target_date: str, tolerance_days: int = 1) -> bool:
        """判断内容日期是否与目标日期相关"""
        try:
            from datetime import datetime, timedelta
            
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