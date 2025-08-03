from abc import ABC, abstractmethod
from typing import Awaitable, Callable

from agents import Tool, function_tool
from loguru import logger

from voice_assistant.tools.decorators import log_tool_decorator


class Toolset(ABC):
    def __init__(self) -> None:
        self._logger = logger.bind(action="tool")

    @abstractmethod
    async def get_tools(self) -> list[Tool]:
        raise NotImplementedError()

    def _wrap_tools(self, *tools_functions: Callable[..., Awaitable[str]]) -> list[Tool]:
        return [function_tool(log_tool_decorator(tool_function, self._logger)) for tool_function in tools_functions]
