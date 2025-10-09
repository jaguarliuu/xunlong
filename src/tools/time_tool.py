"""
 - LLM
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import pytz
import re


class TimeTool:
    """TODO: Add docstring."""

    def __init__(self):
        self.beijing_tz = pytz.timezone('Asia/Shanghai')

    def get_current_time(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
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
        """TODO: Add docstring."""
        weekdays = {
            0: "",
            1: "",
            2: "",
            3: "",
            4: "",
            5: "",
            6: ""
        }
        return weekdays.get(weekday, "")

    def _create_date_entry(self, target: datetime) -> Dict[str, Any]:
        """datetime"""
        return {
            "year": target.year,
            "month": target.month,
            "day": target.day,
            "formatted": target.strftime("%Y-%m-%d")
        }

    def parse_date_query(self, query: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
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

        #  YYYYMMDD / YYYY-MM-DD / YYYY/MM/DD
        date_patterns = [
            r'(\d{4})(\d{1,2})(\d{1,2})',
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

        # 
        if not result["extracted_dates"]:
            lowered = query.lower()
            if any(token in lowered for token in ["", "", "", "", "today"]):
                entry = self._create_date_entry(now)
                result["extracted_dates"].append(entry)
                result["query_contains_date"] = True
                result["relative_reference"] = "today"
            elif any(token in lowered for token in ["", "", "", "yesterday"]):
                entry = self._create_date_entry(now - timedelta(days=1))
                result["extracted_dates"].append(entry)
                result["query_contains_date"] = True
                result["relative_reference"] = "yesterday"
            elif any(token in lowered for token in ["", "day before yesterday"]):
                entry = self._create_date_entry(now - timedelta(days=2))
                result["extracted_dates"].append(entry)
                result["query_contains_date"] = True
                result["relative_reference"] = "day_before_yesterday"
            elif any(token in lowered for token in ["", "", "", "this week"]):
                result["time_filter"] = "week"
                result["relative_reference"] = "this_week"
            elif any(token in lowered for token in ["", "last week"]):
                result["time_filter"] = "week"
                result["relative_reference"] = "last_week"
            elif any(token in lowered for token in ["", "", "this month"]):
                result["time_filter"] = "month"
                result["relative_reference"] = "this_month"

        # 
        if result["extracted_dates"]:
            result["time_filter"] = self._determine_time_filter(result["extracted_dates"], now)

        # 
        if result["query_contains_date"]:
            dates_str = ", ".join([d["formatted"] for d in result["extracted_dates"]])
            filter_desc = f" : {result['time_filter']}" if result.get("time_filter") else ""
            result["time_context"] = (
                f": {dates_str}: {current_time['current_datetime']}"
                f"{filter_desc}"
            )
        else:
            result["time_context"] = (
                f": {current_time['current_datetime']}"
                "''''"
            )

        return result

    def _determine_time_filter(self, extracted_dates: List[Dict[str, Any]], now: datetime) -> Optional[str]:
        """DuckDuckGo"""
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
        """TODO: Add docstring."""
        try:
            content_dt = datetime.strptime(content_date, "%Y-%m-%d")
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")

            diff = abs((content_dt - target_dt).days)
            return diff <= tolerance_days

        except Exception:
            return False

    def format_time_for_search(self, date_info: Dict[str, Any]) -> str:
        """TODO: Add docstring."""
        if not date_info.get("extracted_dates"):
            return ""

        date = date_info["extracted_dates"][0]
        return f"{date['year']}{date['month']}{date['day']}"


# 
time_tool = TimeTool()
