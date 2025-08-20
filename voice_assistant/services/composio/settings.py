from typing import ClassVar

from pydantic import BaseModel, SecretStr

from voice_assistant.app_utils.settings_utils.common import ExtendedConfigDict


class ComposioSettings(BaseModel):
    model_config: ClassVar[ExtendedConfigDict] = {
        "env_prefix": "COMPOSIO_",
        "extra": "ignore",
    }
    composio_api_key: SecretStr
