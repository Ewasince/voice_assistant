import asyncio
import sys
from functools import cache
from typing import Any, Final, NoReturn

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from loguru import logger
from plyer import notification
from uvicorn import Config, Server

from voice_assistant.utils.settings import VASettings
from voxmind.app_interfaces.audio_recognizer import AudioRecognizer
from voxmind.app_interfaces.command_source import CommandSource
from voxmind.app_utils.settings import Settings

logger.remove()  # Удаляем стандартный вывод в stderr
logger.add(sys.stdout, level="DEBUG")  # Добавляем вывод в stdout

LANGFLOW_FLOW_URL: Final[str] = "http://localhost:7860/api/v1/run/efb05274-e31b-4fc7-82a0-761204b898f5?stream=false"


async def main() -> NoReturn:
    load_dotenv()
    settings = VASettings()

    command_sources: list[CommandSource] = [
        get_local_source(settings),
        await get_tg_source(settings),
    ]

    tasks = {asyncio.create_task(source.get_command()): n for n, source in enumerate(command_sources)}

    async def process_command(command_text: str) -> str:
        command_result = make_langflow_request(command_text)

        assistant_response = f"Ответ ассистента > {command_result}"

        if command_result is not None:
            print(assistant_response)
        else:
            print()

        return command_result

    notification.notify(
        title="Ассистент запущен",
        message="Ассистент запущен",
        app_name="Голосовой помощник",
        timeout=10,  # в секундах
    )

    while True:
        done, _ = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            idx = tasks[task]
            result = task.result()

            result = await process_command(result)

            completed_source = command_sources[idx]
            await completed_source.send_response(result)

            new_task = asyncio.create_task(completed_source.get_command())
            del tasks[task]
            tasks[new_task] = idx

    # noinspection PyUnreachableCode
    sys.exit(1)  # Завершение программы с кодом ошибки


def make_langflow_request(input_text: str) -> str:
    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": input_text,
    }

    headers: dict[str, Any] = {}

    # Отправка POST-запроса
    response = requests.post(LANGFLOW_FLOW_URL, json=payload, headers=headers, timeout=100)

    data = response.json()

    return data["outputs"][0]["outputs"][0]["outputs"]["message"]["message"]  # пиздец конечно


@cache
def get_whisper_sst_module() -> AudioRecognizer:
    from voxmind.sst_modules.sst_whisper import WhisperSST

    return WhisperSST(Settings())  # TODO: fix


def get_local_source(settings: Settings) -> CommandSource:
    from voxmind.commands_sources.local_voice_command_source.command_source import LocalVoiceCommandSource

    audio_recognizer = get_whisper_sst_module()
    command_source: CommandSource = LocalVoiceCommandSource(settings, audio_recognizer)
    return command_source


async def get_tg_source(settings: Settings) -> CommandSource:
    from voxmind.commands_sources.telegram_source.command_source import TelegramBotCommandSource

    audio_recognizer = get_whisper_sst_module()
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


if __name__ == "__main__":
    # noinspection PyUnreachableCode
    asyncio.run(main())
