from abc import ABC, abstractmethod

from agents import Tool
from loguru import logger


class Toolset(ABC):
    def __init__(self) -> None:
        self._logger = logger.bind(action="tools")

    @abstractmethod
    async def get_tools(self) -> list[Tool]:
        raise NotImplementedError()
