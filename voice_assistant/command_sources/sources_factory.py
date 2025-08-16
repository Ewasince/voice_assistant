import asyncio
from functools import cache
from typing import Iterable

from fastapi import FastAPI
from loguru import logger
from uvicorn import Config, Server

from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.app_types import DEFAULT_USER_ID, UserId
from voice_assistant.command_sources.enums import CommandSourcesTypes
from voice_assistant.sst_modules.sst_modules_factory import get_sst_module


async def get_sources(user_id: UserId, sources_types: Iterable[CommandSourcesTypes]) -> list[CommandSource]:
    logger.bind(
        user_id=user_id,
        action="src_init",
    ).info(f"Initializing command sources: {', '.join(sources_types)}")

    sources: list[CommandSource] = []
    if CommandSourcesTypes.local_voice in sources_types:
        sources.append(get_local_source())
    if CommandSourcesTypes.telegram in sources_types:
        sources.append(await get_tg_source(user_id))
    if CommandSourcesTypes.web in sources_types:
        sources.append(get_web_source(user_id))

    return sources


@cache
def get_local_source() -> CommandSource:
    from voice_assistant.command_sources.local_voice_command_source.command_source import (  # noqa: PLC0415
        LocalVoiceCommandSource,
    )

    audio_recognizer = get_sst_module()
    command_source: CommandSource = LocalVoiceCommandSource(DEFAULT_USER_ID, audio_recognizer)
    return command_source


@cache
async def get_tg_source(user_id: UserId) -> CommandSource:
    from voice_assistant.command_sources.telegram_source.command_source import get_telegram_bot  # noqa: PLC0415

    telegram_bot = get_telegram_bot()

    command_source = telegram_bot.get_source_for_user(user_id)

    async with telegram_bot.start_bot_lock:
        if not telegram_bot.started:
            await telegram_bot.start()

    return command_source


@cache
def get_web_source(user_id: UserId) -> CommandSource:
    from voice_assistant.command_sources.web_voice_command_source.command_source import (  # noqa: PLC0415
        WebVoiceCommandSource,
    )

    app = FastAPI()
    command_source: CommandSource = WebVoiceCommandSource(user_id, app)

    config = Config(app=app, host="127.0.0.1", port=8010, loop="asyncio")
    server = Server(config)

    asyncio.create_task(server.serve())  # noqa: RUF006
    logger.info("Web api created")
    return command_source
