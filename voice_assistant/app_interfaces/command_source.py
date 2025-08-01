from abc import ABC, abstractmethod
from typing import Self

from voice_assistant.app_utils.types import UserId


class CommandSource(ABC):
    def __init__(self, user_id: UserId):
        self.user_id = user_id

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
