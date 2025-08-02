from agents import Tool

from voice_assistant.app_utils.types import UserId
from voice_assistant.tools.activity_logger.tools import ActivityLogger


async def get_tools(user_id: UserId) -> list[Tool]:
    activity_logger = ActivityLogger(user_id)
    return [*activity_logger.get_tools()]
