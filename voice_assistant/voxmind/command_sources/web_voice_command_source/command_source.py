from fastapi import FastAPI
from loguru import logger

from voice_assistant.voxmind.app_interfaces.command_source import CommandSource
from voice_assistant.voxmind.app_utils.utils import Settings, normalize_text
from voice_assistant.voxmind.command_sources.web_voice_command_source.simple_web import SimpleWebWrapper


class WebVoiceCommandSource(CommandSource):
    def __init__(self, settings: Settings, web_app: FastAPI):
        self.config = settings

        self._web_app_wrapper = SimpleWebWrapper(web_app)

    async def get_command(self) -> str:
        while True:
            text = await self._web_app_wrapper.next_utterance()

            command = self._check_command_after_key_word(text)

            if command is not None:
                break

        return command

    async def send_response(self, text: str) -> None:
        pass

    def _check_command_after_key_word(self, input_text: str | None) -> str | None:
        if input_text is None:
            logger.debug("Ничего не услышал, слушаю дальше...")
            return None

        text = normalize_text(input_text)

        filtered_text = extract_text_after_command(text, self.config.key_phase)

        if not filtered_text:
            logger.debug(f"Не услышал ключевого слова: {text}")
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
