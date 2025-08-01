import httpx
from langchain_core.messages import HumanMessage
from langchain_gigachat.chat_models import GigaChat
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from voice_assistant.app_interfaces.llm_module import LLMClient
from voice_assistant.voxmind.llm_clients.gigachat_client.settings import GigachatSettings


class GigaChatClient(LLMClient):
    def __init__(self) -> None:
        settings = GigachatSettings()

        self._giga = GigaChat(
            model=settings.gigachat_model,
            credentials=settings.gigachat_token.get_secret_value(),
            scope=settings.gigachat_scope,
            verify_ssl_certs=False,
            profanity_check=True,
        )

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
        resp = self._giga.invoke([HumanMessage(content=text)])
        content = resp.content
        if not isinstance(content, str):
            msg = f"cant process: {content}"
            raise ValueError(msg)
        return content
