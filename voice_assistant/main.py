import asyncio
import sys
from typing import Any, Final, NoReturn

import requests
from dotenv import load_dotenv
from loguru import logger
from plyer import notification

from voice_assistant.sources import get_tg_source
from voice_assistant.utils.settings import VASettings
from voxmind.app_interfaces.command_source import CommandSource

logger.remove()  # Удаляем стандартный вывод в stderr
logger.add(sys.stdout, level="DEBUG")  # Добавляем вывод в stdout

LANGFLOW_FLOW_URL: Final[str] = "http://localhost:7860/api/v1/run/efb05274-e31b-4fc7-82a0-761204b898f5?stream=false"


async def main() -> NoReturn:
    load_dotenv()
    settings = VASettings()

    command_sources: list[CommandSource] = [
        # get_local_source(settings),
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
            received_text = task.result()

            generated_text = await process_command(received_text)

            completed_source = command_sources[idx]

            if generated_text:
                await completed_source.send_response(generated_text)

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

    try:
        text_response = data["outputs"][0]["outputs"][0]["outputs"]["message"]["message"]  # пиздец конечно
    except (KeyError, IndexError):
        logger.error(f"{data=}")
        return "Ошибка парсинга ответа от langflow"

    return text_response


if __name__ == "__main__":
    # noinspection PyUnreachableCode
    asyncio.run(main())
