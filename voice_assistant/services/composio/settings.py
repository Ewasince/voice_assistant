from typing import ClassVar

from pydantic import BaseModel, SecretStr

from voice_assistant.app_utils.base_settings import ExtendedConfigDict


class ComposioSettings(BaseModel):
    model_config: ClassVar[ExtendedConfigDict] = {
        "env_prefix": "COMPOSIO_",
        "extra": "ignore",
    }
    composio_api_key: SecretStr
