from voice_assistant.app_interfaces.message_recognizer import TextSource
from voice_assistant.app_utils.settings import Settings


class TextSourceCLI(TextSource):
    def __init__(self):
        self.config = Settings()

    async def next_text_command(self) -> str | None:
        return input("Текстовая команда> ")

