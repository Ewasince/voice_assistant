from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from voice_assistant.app_utils.settings_utils.common import HierarchicalSettings


class TelegramSettings(HierarchicalSettings):
    model_config = SettingsConfigDict(
        env_prefix="TELEGRAM_",
    )
    token: SecretStr
    recognize_voice: bool = True

    user_ids: list[int] = Field(default_factory=list)
