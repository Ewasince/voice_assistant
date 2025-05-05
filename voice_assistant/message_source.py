from voice_assistant.app_interfaces.i_message_recognizer import IMessageRecognizer
from voice_assistant.app_utils.settings import Settings
from voice_assistant.app_utils.utils import normalize_text, extract_text_after_command


class MessageSource:
    """Обрабатывает полученный текст от распознавателя"""

    def __init__(self, recognizer: IMessageRecognizer):
        self.recognizer = recognizer
        self.config = Settings()
        return

    def _prepare_text(self, input_text: str) -> str | None:
        text = normalize_text(input_text)

        filtered_text = extract_text_after_command(text, self.config.key_phase)

        if filtered_text is None:
            # print(f'text not contain phase: {text}')
            return

        return filtered_text

    def _check_command_after_key_word(self, text: str | None) -> str | None:
        if text is None:
            print("Ничего не услышал, слушаю дальше...")
            return

        filtered_text = self._prepare_text(text)
        if filtered_text is None:
            print(f"Не услышал ключевого слова: {text}")
            return

        if filtered_text == "":
            print(f"Не услышал ключевого слова: {text}")
            return

        return filtered_text

    async def wait_command(self) -> str:
        while True:
            text = await self.recognizer.get_audio()

            command = self._check_command_after_key_word(text)

            if command is not None:
                break

        return command
