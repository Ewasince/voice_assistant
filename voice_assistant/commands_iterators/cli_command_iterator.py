from voice_assistant.app_interfaces.command_iterator import CommandIterator
from voice_assistant.app_utils.settings import Settings


class CLICommandIterator(CommandIterator):
    def __init__(self, settings: Settings):
        self.config = settings

    async def __anext__(self) -> str:
        return input("Текстовая команда> ")
