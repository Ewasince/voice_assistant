from voice_assistant.app_interfaces.command_performer import CommandPerformer
from voice_assistant.app_interfaces.llm_module import LLMClient


class CommandLLMQuestion(CommandPerformer):
    def __init__(self, gpt_module: LLMClient):
        self.gpt_module = gpt_module

    async def perform_command(self, command_context: str) -> str | None:
        return self.gpt_module.get_answer(command_context)
