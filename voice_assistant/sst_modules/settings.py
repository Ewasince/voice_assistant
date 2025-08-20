from typing import ClassVar, Literal

from pydantic import BaseModel, SecretStr

from voice_assistant.app_utils.base_settings import ExtendedConfigDict


class SttSettings(BaseModel):
    model_config: ClassVar[ExtendedConfigDict] = {
        "env_prefix": "STT_",
        "extra": "ignore",
    }
    stt_base_url: str
    stt_api_key: SecretStr
    stt_model: str = "stt-openai/whisper-v3-turbo"
    stt_language: str = "ru"

    stt_mode: Literal["local", "api"] = "api"
