import asyncio
from functools import cache

from fastapi import FastAPI
from loguru import logger
from uvicorn import Config, Server

from voice_assistant.app_interfaces.audio_recognizer import AudioRecognizer
from voice_assistant.app_interfaces.command_source import CommandSource


@cache
def _get_whisper_sst_module() -> AudioRecognizer:
    from voice_assistant.sst_modules.sst_whisper import WhisperSST  # noqa: PLC0415

    return WhisperSST()  # TODO: fix


def get_local_source() -> CommandSource:
    from voice_assistant.command_sources.local_voice_command_source.command_source import (  # noqa: PLC0415
        LocalVoiceCommandSource,
    )

    audio_recognizer = _get_whisper_sst_module()
    command_source: CommandSource = LocalVoiceCommandSource(audio_recognizer)
    return command_source


async def get_tg_source() -> CommandSource:
    from voice_assistant.command_sources.telegram_source.command_source import (  # noqa: PLC0415
        TelegramBotCommandSource,
    )

    audio_recognizer = _get_whisper_sst_module()
    command_source = TelegramBotCommandSource(audio_recognizer)
    await command_source.start()

    return command_source


def get_web_source() -> CommandSource:
    from voice_assistant.command_sources.web_voice_command_source.command_source import (  # noqa: PLC0415
        WebVoiceCommandSource,
    )

    app = FastAPI()
    command_source: CommandSource = WebVoiceCommandSource(app)

    config = Config(app=app, host="127.0.0.1", port=8010, loop="asyncio")
    server = Server(config)

    asyncio.create_task(server.serve())  # noqa: RUF006
    logger.info("Web api created")
    return command_source
