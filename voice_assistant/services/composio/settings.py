from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

from voice_assistant.app_utils.settings_utils.common import HierarchicalSettings


class ComposioSettings(HierarchicalSettings):
    model_config = SettingsConfigDict(
        env_prefix="COMPOSIO_",
    )
    api_key: SecretStr
