from loguru import logger

from voice_assistant.agent.openai_agent import UserAgent, get_agent
from voice_assistant.app_utils.app_types import CommandPerformerFunction, UserId


async def get_performer(user_id: UserId) -> CommandPerformerFunction:
    logger.bind(
        user_id=user_id,
        action="prf_init",
    ).info("Initializing command performer")

    agent = await get_agent(user_id)
    command_performer = CommandPerformer(user_id, agent)

    return command_performer.perform_command  # TODO: will gc fights with it?


class CommandPerformer:
    """
    Wraps agent request-response logic
    """

    def __init__(self, user_id: UserId, agent: UserAgent):
        self._user_id = user_id
        self._user_agent: UserAgent = agent

    async def perform_command(self, command_text: str) -> str | None:
        command_result = await self._user_agent.run_agent(command_text)

        if command_result is not None:
            print(f"Ответ ассистента > {command_result}")
        else:
            print()

        return command_result
