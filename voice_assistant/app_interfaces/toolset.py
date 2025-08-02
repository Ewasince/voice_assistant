from abc import ABC, abstractmethod

from agents import Tool


class Toolset(ABC):
    @abstractmethod
    async def get_tools(self) -> list[Tool]:
        raise NotImplementedError()
