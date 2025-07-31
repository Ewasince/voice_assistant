import asyncio
import sys
from typing import NoReturn

from dotenv import load_dotenv
from loguru import logger
from plyer import notification

from voice_assistant.command_processer import process_command, settings
from voice_assistant.sources import get_local_source, get_tg_source
from voxmind.app_interfaces.command_source import CommandSource

logger.remove()  # Удаляем стандартный вывод в stderr
logger.add(sys.stdout, level="DEBUG")  # Добавляем вывод в stdout


async def main() -> NoReturn:
    load_dotenv()

    command_sources = await get_sources()

    startup_completed()

    await message_loop(command_sources)

    # noinspection PyUnreachableCode
    sys.exit(1)


async def get_sources() -> list[CommandSource]:
    return [
        get_local_source(settings),
        await get_tg_source(settings),
    ]


def startup_completed() -> None:
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
