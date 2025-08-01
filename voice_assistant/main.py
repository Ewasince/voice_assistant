import asyncio
import sys
from typing import NoReturn

from dotenv import load_dotenv
from loguru import logger
from plyer import notification

from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.settings import primary_settings
from voice_assistant.app_utils.types import DEFAULT_USER_ID
from voice_assistant.command_processer import process_command
from voice_assistant.command_sources.sources import get_sources

logger.remove()  # Удаляем стандартный вывод в stderr
logger.add(sys.stdout, level="DEBUG")  # Добавляем вывод в stdout


async def main() -> NoReturn:
    load_dotenv()

    logger.info("Starting voice assistant")

    sources_to_use = primary_settings.sources_to_use_list
    command_sources = await get_sources(DEFAULT_USER_ID, sources_to_use)

    startup_completed()

    await message_loop(command_sources)

    # noinspection PyUnreachableCode
    sys.exit(1)


def startup_completed() -> None:
    logger.info("Startup completed!")
    notification.notify(
        title="Ассистент запущен",
        message="Ассистент запущен",
        app_name="Голосовой помощник",
        timeout=10,  # в секундах
    )


async def message_loop(command_sources: list[CommandSource]) -> NoReturn:
    tasks = {asyncio.create_task(source.get_command()): n for n, source in enumerate(command_sources)}
    while True:
        done, _ = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            idx = tasks[task]
            received_text = task.result()

            generated_text = await process_command(received_text)

            completed_source = command_sources[idx]

            if generated_text:
                await completed_source.send_response(generated_text)

            new_task = asyncio.create_task(completed_source.get_command())
            del tasks[task]
            tasks[new_task] = idx


if __name__ == "__main__":
    # noinspection PyUnreachableCode
    asyncio.run(main())
