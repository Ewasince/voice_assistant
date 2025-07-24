import asyncio
from functools import cache

from fastapi import FastAPI
from loguru import logger
from uvicorn import Config, Server

from voxmind.app_interfaces.audio_recognizer import AudioRecognizer
from voxmind.app_interfaces.command_source import CommandSource
from voxmind.app_utils.settings import Settings


@cache
def _get_whisper_sst_module() -> AudioRecognizer:
    from voxmind.sst_modules.sst_whisper import WhisperSST

    return WhisperSST(Settings())  # TODO: fix


def get_local_source(settings: Settings) -> CommandSource:
    from voxmind.commands_sources.local_voice_command_source.command_source import LocalVoiceCommandSource

    audio_recognizer = _get_whisper_sst_module()
    command_source: CommandSource = LocalVoiceCommandSource(settings, audio_recognizer)
    return command_source


async def get_tg_source(settings: Settings) -> CommandSource:
    from voxmind.commands_sources.telegram_source.command_source import TelegramBotCommandSource

    audio_recognizer = _get_whisper_sst_module()
    command_source = TelegramBotCommandSource(settings, audio_recognizer)
    await command_source.start()

    return command_source


def get_web_source(settings: Settings) -> CommandSource:
    from voxmind.commands_sources.web_voice_command_source.command_source import WebVoiceCommandSource

    app = FastAPI()
    command_source: CommandSource = WebVoiceCommandSource(settings, app)

    config = Config(app=app, host="127.0.0.1", port=8010, loop="asyncio")
    server = Server(config)

    asyncio.create_task(server.serve())  # noqa: RUF006
    logger.info("Web api created")
    return command_source
