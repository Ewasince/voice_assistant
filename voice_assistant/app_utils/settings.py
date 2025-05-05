import pyaudio
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Основной класс конфига, выполняющий проверку всех полей
    """

    # secrets

    gigachat_token: str | None = Field(default=None)

    # public config
    data_dir: str = Field(default="data")

    ## audio settings
    chunk: int = Field(default=1024)
    sample_format: int = Field(default=pyaudio.paInt16)
    channels: int = Field(default=2)
    rate: int = Field(default=44100)

    ## recognizing settings
    key_phase: str = Field(default="папич")
    regexp: str = Field(default=r"[^A-Za-zА-ЯЁа-яё0-9 ]")
    language: str = "ru-RU"
