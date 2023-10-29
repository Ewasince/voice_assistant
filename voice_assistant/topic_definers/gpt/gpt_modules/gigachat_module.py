from gigachat import GigaChat

from voice_assistant.topic_definers.gpt.gpt_modules.i_gpt_module import IGPTModule


class GigaChatModule(IGPTModule):
    def __init__(self, credentials: str):
        self.credential = credentials

    def get_answer(self, text) -> str:
        # Используйте токен, полученный в личном кабинете из поля Авторизационные данные
        with GigaChat(credentials=self.credential, verify_ssl_certs=False) as giga:
            response = giga.chat(text)
            text = response.choices[0].message.content

            return text


if __name__ == "__main__":
    gc = GigaChatModule(input())

    while True:
        print(gc.get_answer(input()))

    pass
