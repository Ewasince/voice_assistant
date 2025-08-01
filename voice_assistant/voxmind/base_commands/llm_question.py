from voice_assistant.app_interfaces.command_performer import CommandPerformer
from voice_assistant.app_interfaces.llm_module import LLMClient
from voice_assistant.voxmind.assistant_core.context import Context


class CommandLLMQuestion(CommandPerformer):
    def __init__(self, gpt_module: LLMClient):
        self.gpt_module = gpt_module

    async def perform_command(self, command_text: str, _: Context) -> str | None:
        return self.gpt_module.get_simple_answer(command_text)
