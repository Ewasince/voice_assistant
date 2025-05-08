from voice_assistant.app_interfaces.command_iterator import CommandIterator
from voice_assistant.app_utils.settings import Settings
from voice_assistant.app_utils.utils import normalize_text
from voice_assistant.commands_iterators.voice_command_iterator.stt_module import STTModule


class VoiceCommandIterator(CommandIterator):
    # TODO: разделить класс на распознаватель и источник аудио
    def __init__(self, settings: Settings, *, setup_micro: bool = True):
        self.config = settings

        self._sst_module = STTModule(settings, setup_micro=setup_micro)

    async def __anext__(self) -> str:
        while True:
            text = await self._sst_module.next_utterance()

            command = self._check_command_after_key_word(text)

            if command is not None:
                break

        return command

    def _check_command_after_key_word(self, input_text: str | None) -> str | None:
        if input_text is None:
            print("Ничего не услышал, слушаю дальше...")
            return None

        text = normalize_text(input_text)

        filtered_text = extract_text_after_command(text, self.config.key_phase)

        if not filtered_text:
            print(f"Не услышал ключевого слова: {text}")
            return None

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
