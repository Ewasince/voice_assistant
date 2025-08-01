import httpx
import ollama
from loguru import logger
from ollama import ChatResponse
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from voice_assistant.voxmind.app_interfaces.llm_module import LLMClient
from voice_assistant.voxmind.app_utils.utils import Settings


class LocalLLMClient(LLMClient):
    def __init__(self, settings: Settings):
        self._settings = settings

    @retry(
        retry=retry_if_exception_type(httpx.ConnectError),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=lambda retry_state: logger.debug(
            f"Fail to request llm #{retry_state.attempt_number}, retry in "
            f"{retry_state.next_action.sleep if retry_state.next_action else 0:.1f}"
        ),
    )
    def get_simple_answer(self, text: str) -> str:
        response: ChatResponse = ollama.chat(
            model=self._settings.ollama_model,
            messages=[
                {
                    "role": "user",
                    "content": text,
                },
            ],
        )
        if not isinstance(response.message.content, str):
            raise ValueError(f"doesnt match type: {type(response.message.content)}")
        return response.message.content


if __name__ == "__main__":
    response: ChatResponse = ollama.chat(
        model="llama3:8b",
        messages=[
            {
                "role": "user",
                "content": "привет как дела?",
            },
        ],
    )
    res = response.message.content
    print(res)
