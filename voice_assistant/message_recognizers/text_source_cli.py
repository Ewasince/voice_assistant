from voice_assistant.app_interfaces.message_recognizer import TextSource
from voice_assistant.app_utils.settings import Settings


class TextSourceCLI(TextSource):
    # TODO: разделить класс на распознаватель и источник аудио
    def __init__(self):
        self.config = Settings()

    async def next_text_command(self) -> str | None:
        return input("Что я услышал> ")

