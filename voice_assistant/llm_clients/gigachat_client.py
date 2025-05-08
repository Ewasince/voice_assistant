from typing import ClassVar

from langchain_core.messages import HumanMessage
from langchain_gigachat.chat_models import GigaChat

from voice_assistant.app_interfaces.llm_module import LLMClient
from voice_assistant.app_utils.settings import Settings


class GigaChatClient(LLMClient):
    SCOPE: ClassVar[str] = "GIGACHAT_API_PERS"
    MODEL: ClassVar[str] = "GigaChat-2"
    # SYSTEM_PROMPT: ClassVar[str] = (
    #     "Ты — эксперт-лингвист, отлично разбирающийся в словообразовании, орфографии и значении слов, включая сленг, "
    #     "просторечие и разговорные формы. Твоя задача — преобразовать любое данное слово или выражение в его "
    #     "нормативную (литературную) форму: корректное слово, в правильном числе, падеже и без искажений. "
    #     "Отвечай кратко, точно и по делу — только нормализованная форма слова без пояснений."
    # )

    def __init__(self, settings: Settings):
        self._giga = GigaChat(
            model=self.MODEL,
            credentials=settings.gigachat_token,
            scope=self.SCOPE,
            verify_ssl_certs=False,
            profanity_check=True,
        )

    def get_answer(self, text: str) -> str:
        resp = self._giga.invoke([HumanMessage(content=text)])
        content = resp.content
        if not isinstance(content, str):
            msg = f"cant process: {content}"
            raise ValueError(msg)
        return content


if __name__ == "__main__":
    gc = GigaChatClient(Settings())

    while True:
        print(gc.get_answer(input()))
