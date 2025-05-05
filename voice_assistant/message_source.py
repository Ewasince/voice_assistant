from voice_assistant.app_interfaces.message_recognizer import TextSource
from voice_assistant.app_utils.settings import Settings
from voice_assistant.app_utils.utils import normalize_text


class MessageSource:
    """Обрабатывает полученный текст от распознавателя"""

    def __init__(self, recognizer: TextSource):
        self.recognizer = recognizer
        self.config = Settings()
        return

    async def wait_command(self) -> str:
        while True:
            text = await self.recognizer.next_text_command()

            command = self._check_command_after_key_word(text)

            if command is not None:
                break

        return command

    def _check_command_after_key_word(self, input_text: str | None) -> str | None:
        if input_text is None:
            print("Ничего не услышал, слушаю дальше...")
            return

        text = normalize_text(input_text)

        filtered_text = extract_text_after_command(text, self.config.key_phase)

        if not filtered_text:
            print(f"Не услышал ключевого слова: {text}")
            return

        return filtered_text


def extract_text_after_command(text: str, key: str | None) -> str | None:
    if not key:
        return text.strip()

    pos = text.find(key)
    if pos == -1:
        return None

    pos = pos + len(key) + 1

    filtered_text = text[pos:]

    return filtered_text.strip()
