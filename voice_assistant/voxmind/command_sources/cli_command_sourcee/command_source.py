from voice_assistant.app_interfaces.command_source import CommandSource


class CLICommandSource(CommandSource):
    async def get_command(self) -> str:
        command_utterance = ""
        while not command_utterance:
            command_utterance = await self._get_text_input()
        return command_utterance

    async def send_response(self, text: str) -> None:
        pass

    async def _get_text_input(self) -> str:
        return input("Текстовая команда> ")
