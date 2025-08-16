import asyncio
from functools import cache

from fastapi import FastAPI
from loguru import logger
from uvicorn import Config, Server

from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.app_types import UserId


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
