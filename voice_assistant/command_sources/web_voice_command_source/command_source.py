import asyncio

from fastapi import FastAPI
from loguru import logger
from uvicorn import Config, Server

from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.settings import primary_settings
from voice_assistant.app_utils.types import UserId
from voice_assistant.app_utils.utils import normalize_text
from voice_assistant.command_sources.web_voice_command_source.simple_web import SimpleWebWrapper


class WebVoiceCommandSource(CommandSource):
    def __init__(self, user_id: UserId, web_app: FastAPI):
        super().__init__(user_id)
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

        filtered_text = extract_text_after_command(text, primary_settings.key_phase)

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


def get_web_source(user_id: UserId) -> CommandSource:
    app = FastAPI()
    command_source: CommandSource = WebVoiceCommandSource(user_id, app)

    config = Config(app=app, host="127.0.0.1", port=8010, loop="asyncio")
    server = Server(config)

    asyncio.create_task(server.serve())  # noqa: RUF006
    logger.info("Web api created")
    return command_source
