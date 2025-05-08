from voice_assistant.app_interfaces.command_performer import CommandPerformer
from voice_assistant.app_interfaces.llm_module import LLMClient
from voice_assistant.assistant_core.context import Context


class CommandTimeKeeperGoogle(CommandPerformer):
    def __init__(self, gpt_module: LLMClient):
        self.gpt_module = gpt_module

    async def perform_command(self, command_text: str, _: Context) -> str | None:
        raise NotImplementedError
