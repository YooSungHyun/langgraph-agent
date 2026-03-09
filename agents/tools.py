from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_datetime() -> str:
    """현재 날짜와 시간을 반환한다."""
    return datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 %S초")


TOOLS = [get_current_datetime]
