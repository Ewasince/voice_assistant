from pydantic import SecretStr

from voice_assistant.app_utils.app_types import DEFAULT_USER_ID, UserId
from voice_assistant.app_utils.base_settings import ExtendedSettings
from voice_assistant.command_sources.enums import CommandSourcesTypes


class Settings(ExtendedSettings):
    debug_mode: bool = False

    # database
    database_uri: str = "sqlite:///data/data.db"

    composio_api_key: SecretStr

    # recognizing settings
    key_phase: str = "помощник"
    regexp: str = r"[^A-Za-zА-ЯЁа-яё0-9 ]"
    language: str = "ru"

    # example recognizers settings
    use_gpu: bool = False
    whisper_model: str = "turbo"

    # local llm settings
    ollama_model: str = "llama3:8b"

    sources_to_use_list: tuple[CommandSourcesTypes, ...] = (CommandSourcesTypes.telegram,)
    active_users_list: tuple[UserId, ...] = (DEFAULT_USER_ID,)


# noinspection PyArgumentList
primary_settings = Settings()
