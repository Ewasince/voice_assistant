from voice_assistant.app_interfaces.command_performer import ICommandPerformer
from voice_assistant.app_interfaces.gpt_module import LLMModule


class CommandLLMQuestion(ICommandPerformer):
    def __init__(self, gpt_module: LLMModule):
        self.gpt_module = gpt_module

    async def perform_command(self, command_context: str) -> str | None:
        return self.gpt_module.get_answer(command_context)
