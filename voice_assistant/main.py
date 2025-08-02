import asyncio
import contextlib
import sys
from typing import AsyncGenerator, NoReturn

from dotenv import load_dotenv
from loguru import logger
from plyer import notification

from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.settings import primary_settings
from voice_assistant.app_utils.types import CommandPerformerFunction, UserId
from voice_assistant.command_performers.performer_factory import get_performer
from voice_assistant.command_sources.sources_factory import get_sources

logger.remove()  # Удаляем стандартный вывод в stderr
logger.add(sys.stdout, level="DEBUG")  # Добавляем вывод в stdout


async def main() -> NoReturn:
    load_dotenv()

    logger.info("Starting voice assistant")

    logger.info("Initializing sources")
    sources_to_use = primary_settings.sources_to_use_list
    sources_by_users = {
        user_id: await get_sources(user_id, sources_to_use) for user_id in primary_settings.active_users_list
    }

    logger.info("Initializing performers")
    performers_by_users = {user_id: await get_performer(user_id) for user_id in primary_settings.active_users_list}

    loops = []

    for user_id in primary_settings.active_users_list:
        command_sources = sources_by_users[user_id]
        command_performer = performers_by_users[user_id]
        # noinspection PyUnreachableCode
        loops.append(asyncio.create_task(message_loop(user_id, command_sources, command_performer)))

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


async def message_loop(
    user_id: UserId,
    command_sources: list[CommandSource],
    command_performer: CommandPerformerFunction,
) -> NoReturn:
    logger.info(f"Start messages loop for user: {user_id}")
    tasks = {asyncio.create_task(source.get_interaction_gen()): n for n, source in enumerate(command_sources)}
    while True:
        done, _ = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            idx = tasks[task]
            interaction_gen: AsyncGenerator[str, str] = task.result()

            received_text = await anext(interaction_gen)

            generated_text = await command_performer(received_text)

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
