from voice_assistant.app_interfaces.command_performer import ICommandPerformer
from voice_assistant.app_interfaces.gpt_module import IGPTModule


class CommandGPTDefault(ICommandPerformer):
    def __init__(self, gpt_module: IGPTModule):
        self.gpt_module = gpt_module

    def get_command_topic(self) -> None:
        return None

    async def perform_command(self, command_context: str) -> str | None:
        return self.gpt_module.get_answer(command_context)
