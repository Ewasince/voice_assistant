from abc import ABC, abstractmethod
from typing import Self


class CommandSource(ABC):
    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> str:
        return await self.get_command()

    @abstractmethod
    async def get_command(self) -> str:
        pass

    @abstractmethod
    async def send_response(self, text: str) -> None:
        pass
