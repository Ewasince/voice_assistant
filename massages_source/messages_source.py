from app_interfaces.i_messages_recognizer import IMessagesRecognizer
from app_interfaces.i_messages_source import IMessagesSource
from app_utils.config import Config
from app_utils.utils import normalize_text, extract_text_after_command


class MessagesSourceLocalMic(IMessagesSource):
    def __init__(self, recognizer: IMessagesRecognizer):
        self.recognizer = recognizer
        self.config = Config()
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

    def wait_command(self) -> str:
        while True:
            text = self.recognizer.get_audio()

            command = self._check_command_after_key_word(text)

            if command is not None:
                break

        return command
