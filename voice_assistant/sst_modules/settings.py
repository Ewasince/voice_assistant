from typing import ClassVar, Literal

from pydantic import BaseModel, SecretStr
from pydantic_settings import SettingsConfigDict

from voice_assistant.app_utils.settings_utils.common import ExtendedConfigDict, HierarchicalSettings


class SttSettings(HierarchicalSettings):
    model_config = SettingsConfigDict(
        env_prefix="STT_",
    )
    stt_base_url: str
    stt_api_key: SecretStr
    stt_model: str = "stt-openai/whisper-v3-turbo"
    stt_language: str = "ru"

    stt_mode: Literal["local", "api"] = "api"
