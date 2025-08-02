from agents import Tool

from voice_assistant.app_utils.types import UserId


async def get_tools(user_id: UserId) -> list[Tool]:
    raise NotImplementedError
