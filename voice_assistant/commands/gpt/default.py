from voice_assistant.app_interfaces.i_command_performer import ICommandPerformer
from voice_assistant.topic_definers.gpt.gpt_modules.i_gpt_module import IGPTModule


class CommandGPTDefault(ICommandPerformer):
    def __init__(self, gpt_module: IGPTModule):
        self.gpt_module = gpt_module
        return

    def get_command_topic(self) -> None:
        return None

    async def perform_command(self, command_context: str) -> str | None:
        res = self.gpt_module.get_answer(command_context)
        return res
