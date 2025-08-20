from typing import Literal

from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

from voice_assistant.app_utils.settings_utils.common import HierarchicalSettings


class SttSettings(HierarchicalSettings):
    model_config = SettingsConfigDict(
        env_prefix="STT_",
    )
    base_url: str
    api_key: SecretStr
    model: str = "stt-openai/whisper-v3-turbo"
    language: str = "ru"

    mode: Literal["local", "api"] = "api"
