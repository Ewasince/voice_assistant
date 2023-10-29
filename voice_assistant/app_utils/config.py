import os

import pyaudio
from pydantic import BaseModel, Field


class Config(BaseModel):
    """
    Основной класс конфига, выполняющий проверку всех полей
    """

    def __new__(cls):
        if hasattr(cls, "_instance"):
            return cls._instance

        # создание конфига
        config_dict = {}

        for param in cls.model_fields:
            param: str
            var = os.environ.get(param.upper())
            if var is not None:
                config_dict[param] = var

        cls._instance = super(Config, cls).__new__(cls)
        super(Config, cls._instance).__init__(**config_dict)

        return cls._instance

    # noinspection PyMissingConstructor
    def __init__(self, *args, **kwargs):
        pass

    ####################

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
