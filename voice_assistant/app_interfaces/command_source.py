from abc import ABC, abstractmethod
from typing import AsyncGenerator, Self, final

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

    @final
    async def get_interaction_gen(self) -> AsyncGenerator[str, str]:
        gen = self._user_bot_interaction()
        await anext(gen)  # first yield None
        return gen  # type: ignore[return-value]

    async def _user_bot_interaction(self) -> AsyncGenerator[str | None, str]:
        res = await self.get_command()
        yield None  # first yield None
        response = yield res
        await self.send_response(response)
