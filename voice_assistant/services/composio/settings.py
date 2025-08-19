from pydantic import SecretStr

from voice_assistant.app_utils.base_settings import ExtendedSettings


class Settings(ExtendedSettings):
    composio_api_key: SecretStr


# noinspection PyArgumentList
composio_settings = Settings()
