from typing import Any

from pydantic import SecretStr
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
)

from voice_assistant.command_sources.enums import CommandSourcesTypes


class ListableSource(EnvSettingsSource):
    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        if field_name.lower().endswith("_list"):
            return list(value.split(","))
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):
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
    telegram_token: str = ""
    telegram_chat_id: int = 0

    # local llm settings
    ollama_model: str = "llama3:8b"

    sources_to_use_list: list[CommandSourcesTypes] = [CommandSourcesTypes.telegram]

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        env_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (ListableSource(settings_cls),)


# noinspection PyArgumentList
primary_settings = Settings()
