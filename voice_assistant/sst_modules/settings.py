from typing import Literal

from pydantic import SecretStr

from voice_assistant.app_utils.base_settings import ExtendedSettings


class Settings(ExtendedSettings):
    stt_base_url: str
    stt_api_key: SecretStr
    stt_model: SecretStr = SecretStr("stt-openai/whisper-v3-turbo")
    stt_language: str = "ru"

    stt_mode: Literal["local", "api"] = "api"

    # calendar_settings: CalendarSettings = lazy(CalendarSettings)


# noinspection PyArgumentList
stt_settings = Settings()
