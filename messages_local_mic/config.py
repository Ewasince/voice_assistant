import os

import pyaudio
from pydantic import BaseModel, Field


class Config(BaseModel):
    """
    Основной класс конфига, выполняющий проверку всех полей
    """

    # secrets

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

    # делаем конфиг неизменяемым
    class Config:
        frozen = True

    pass


# создание конфига
__config_dict = {}

for param in Config.model_fields:
    param: str
    var = os.environ.get(param.upper())
    if var is not None:
        __config_dict[param] = var
    pass

config: Config = Config(**__config_dict)
