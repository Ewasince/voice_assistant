from typing import Awaitable, Callable

from loguru import logger

from voice_assistant.agent.openai_agent import UserAgent, get_agent
from voice_assistant.app_utils.types import UserId


async def get_performer(user_id: UserId) -> Callable[[str], Awaitable[str]]:
    logger.info(f"Initializing for user '{user_id}' command performer")

    command_performer = CommandPerformer(user_id)
    await command_performer.setup_agent()

    return command_performer.run_agent  # TODO: will gc fights with it?


class CommandPerformer:
    """
    Wraps agent request-response logic
    """

    def __init__(self, user_id: UserId):
        self._user_id = user_id

        self._user_agent: UserAgent | None = None

    async def setup_agent(self) -> None:
        self._user_agent = await get_agent(self._user_id)

    async def run_agent(self, input_text: str) -> str:
        if self._user_agent is None:
            raise ValueError("Agent not initialized!")

        command_result = await self._user_agent.run_agent(input_text)

        assistant_response = f"Ответ ассистента > {command_result}"

        if command_result is not None:
            print(assistant_response)
        else:
            print()

        return command_result
