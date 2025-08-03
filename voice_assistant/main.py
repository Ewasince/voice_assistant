import asyncio
import contextlib
import sys
import traceback
from typing import Any, AsyncGenerator, Awaitable, NoReturn

from dotenv import load_dotenv
from loguru import logger
from plyer import notification

from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.settings import primary_settings
from voice_assistant.app_utils.types import DEFAULT_USER_ID, CommandPerformerFunction, UserId
from voice_assistant.command_performers.performer_factory import get_performer
from voice_assistant.command_sources.sources_factory import get_sources

logger.remove()  # Удаляем стандартный вывод в stderr


def fmt(record: Any) -> str:
    record["extra"].setdefault("user_id", "<no_user>")

    format_str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {extra[user_id]: <9} | "

    if "action" in record["extra"]:
        record["extra"]["action"] = record["extra"]["action"].upper()
        format_str += "<cyan>{extra[action]: <9}</cyan> | "
    else:
        format_str += "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "

    format_str += "<level>{message}</level>"

    format_str += "\n"

    return format_str


logger.add(
    sys.stdout,
    level="DEBUG",
    format=fmt,
)


async def main() -> Awaitable[NoReturn]:
    load_dotenv()

    logger.info("Starting voice assistant")

    loops_tasks = []

    for user_id in primary_settings.active_users_list:
        loops_tasks.append(asyncio.create_task(setup_user_and_start_loop(user_id)))

    while loops_tasks:
        done, _ = await asyncio.wait(loops_tasks, return_when=asyncio.FIRST_EXCEPTION)
        for task in done:
            loops_tasks.remove(task)

            exc = task.exception()
            if not exc:
                continue

            logger.error(f"Task {task} ends with exception: {exc}")
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)

    sys.exit(0)


async def setup_user_and_start_loop(user_id: UserId) -> Awaitable[NoReturn]:
    try:
        sources_to_use = primary_settings.sources_to_use_list
        command_sources = await get_sources(user_id, sources_to_use)

        command_performer = await get_performer(user_id)

        startup_completed(user_id)

        return await message_loop(user_id, command_sources, command_performer)
    except Exception as e:
        logger.bind(user_id=user_id).exception(f"exception in user loop: {e}")
        raise e


def startup_completed(user_id: UserId) -> None:
    logger.bind(user_id=user_id).success("Startup completed!")

    if user_id == DEFAULT_USER_ID:
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
) -> Awaitable[NoReturn]:
    logger.bind(user_id=user_id).info("Start messages loop")
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
