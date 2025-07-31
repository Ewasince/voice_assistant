from typing import Any, Final

import requests
from loguru import logger

from voice_assistant.agent.openai_agent import run_agent
from voice_assistant.settings import VASettings

LANGFLOW_FLOW_URL_TEMPLATE: Final[str] = "http://localhost:7860/api/v1/run/{}?stream=false"
settings = VASettings()


async def process_command(command_text: str) -> str:
    command_result = await make_open_ai_request(command_text)

    assistant_response = f"Ответ ассистента > {command_result}"

    if command_result is not None:
        print(assistant_response)
    else:
        print()

    return command_result


async def make_open_ai_request(input_text: str) -> str:
    return await run_agent(input_text)


def make_langflow_request(input_text: str) -> str:
    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": input_text,
        "session_id": settings.langflow_session_id,
    }

    headers: dict[str, Any] = {}

    # Отправка POST-запроса
    response = requests.post(
        LANGFLOW_FLOW_URL_TEMPLATE.format(settings.langflow_flow_id), json=payload, headers=headers, timeout=100
    )

    data = response.json()

    try:
        text_response = data["outputs"][0]["outputs"][0]["outputs"]["message"]["message"]  # пиздец конечно
    except (KeyError, IndexError):
        logger.error(f"{data=}")
        return "Ошибка парсинга ответа от langflow"

    return text_response
