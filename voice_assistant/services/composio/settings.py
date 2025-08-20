from typing import ClassVar

from pydantic import BaseModel, SecretStr
from pydantic_settings import SettingsConfigDict

from voice_assistant.app_utils.settings_utils.common import ExtendedConfigDict, HierarchicalSettings


class ComposioSettings(HierarchicalSettings):
    model_config = SettingsConfigDict(
        env_prefix="COMPOSIO_",
    )
    composio_api_key: SecretStr
