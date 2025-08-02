import asyncio
from itertools import chain

from agents import Tool

from voice_assistant.app_utils.types import UserId
from voice_assistant.tools.activity_logger.tools import get_activity_logger


async def get_tools(user_id: UserId) -> list[Tool]:
    toolsets = await asyncio.gather(
        get_activity_logger(user_id),
        # more tools in plans...
    )

    tools_lists = await asyncio.gather(*(toolset.get_tools() for toolset in toolsets))

    return list(chain.from_iterable(tools_lists))
