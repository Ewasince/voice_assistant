import asyncio
import sys
import traceback
from itertools import chain

from agents import Tool
from loguru import logger

from voice_assistant.app_interfaces.toolset import Toolset
from voice_assistant.app_utils.app_types import UserId
from voice_assistant.tools.activity_logger.factory import get_activity_logger


async def get_tools(user_id: UserId) -> list[Tool]:
    gather_results = await asyncio.gather(
        get_activity_logger(user_id),
        # more tools in plans...
        return_exceptions=True,
    )

    toolsets: list[Toolset] = []

    for gather_result in gather_results:
        if isinstance(gather_result, Toolset):
            toolsets.append(gather_result)
            continue
        if not isinstance(gather_result, Exception):
            raise ValueError(f"invalid gather_result '{type(gather_result)}': {gather_result}")
        logger.bind(user_id=user_id).opt(exception=gather_result).error(f"fail to load toolset: {gather_result}")
        traceback.print_exception(type(gather_result), gather_result, gather_result.__traceback__, file=sys.stderr)

    tools_lists = await asyncio.gather(*(toolset.get_tools() for toolset in toolsets))

    return list(chain.from_iterable(tools_lists))
