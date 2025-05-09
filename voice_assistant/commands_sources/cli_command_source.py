from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.settings import Settings


class CLICommandSource(CommandSource):
    def __init__(self, settings: Settings):
        self.config = settings

    async def __anext__(self) -> str:
        command_utterance = ""
        while not command_utterance:
            command_utterance = await self._get_text_input()
        return command_utterance

    async def _get_text_input(self) -> str:
        return input("Текстовая команда> ")
