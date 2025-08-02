import asyncio
import contextlib
import sys
from typing import AsyncGenerator, NoReturn

from dotenv import load_dotenv
from loguru import logger
from plyer import notification

from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.settings import primary_settings
from voice_assistant.app_utils.types import DEFAULT_USER_ID, UserId
from voice_assistant.command_processer import process_command
from voice_assistant.command_sources.sources import get_sources

logger.remove()  # Удаляем стандартный вывод в stderr
logger.add(sys.stdout, level="DEBUG")  # Добавляем вывод в stdout


async def main() -> NoReturn:
    load_dotenv()

    logger.info("Starting voice assistant")

    sources_to_use = primary_settings.sources_to_use_list

    sources_by_users = {
        user_id: await get_sources(user_id, sources_to_use)
        for user_id in [
            DEFAULT_USER_ID,
        ]
    }

    # noinspection PyUnreachableCode
    loops = [
        asyncio.create_task(message_loop(user_id, command_sources))
        for user_id, command_sources in sources_by_users.items()
    ]

    startup_completed()

    await asyncio.wait(loops, return_when=asyncio.ALL_COMPLETED)

    sys.exit(0)


def startup_completed() -> None:
    logger.success("Startup completed!")
    notification.notify(
        title="Ассистент запущен",
        message="Ассистент запущен",
        app_name="Голосовой помощник",
        timeout=10,  # в секундах
    )


async def message_loop(user_id: UserId, command_sources: list[CommandSource]) -> NoReturn:
    logger.info(f"Start messages loop for user: {user_id}")
    tasks = {asyncio.create_task(source.get_interaction_gen()): n for n, source in enumerate(command_sources)}
    while True:
        done, _ = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            idx = tasks[task]
            interaction_gen: AsyncGenerator[str, str] = task.result()

            received_text = await anext(interaction_gen)

            generated_text = await process_command(received_text)

            completed_source = command_sources[idx]

            if generated_text:
                with contextlib.suppress(StopAsyncIteration):
                    await interaction_gen.asend(generated_text)
            else:
                await interaction_gen.aclose()

            new_task = asyncio.create_task(completed_source.get_interaction_gen())
            del tasks[task]
            tasks[new_task] = idx


if __name__ == "__main__":
    # noinspection PyUnreachableCode
    asyncio.run(main())
