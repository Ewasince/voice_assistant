from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # recognizing settings
    key_phase: str = Field(default="помощник")
    regexp: str = Field(default=r"[^A-Za-zА-ЯЁа-яё0-9 ]")
    language: str = "ru"

    # example recognizers settings
    use_gpu: bool = Field(default=False)
    whisper_model: str = Field(default="base")
    telegram_token: str = Field(default="")
    telegram_chat_id: int = Field(default=0)

    # local llm settings
    ollama_model: str = Field(default="llama3:8b")


primary_settings = Settings()
