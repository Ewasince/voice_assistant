from __future__ import annotations

from functools import cache
from typing import ClassVar

from voice_assistant.agent.settings import AgentSettings
from voice_assistant.app_utils.app_types import DEFAULT_USER_ID, UserId
from voice_assistant.app_utils.base_settings import HierarchicalSettings, lazy_nested
from voice_assistant.command_sources.enums import CommandSourcesTypes


class Settings(HierarchicalSettings):
    debug_mode: bool = False

    # database
    database_uri: str = "sqlite:///data/data.db"

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

    agent_settings: ClassVar[AgentSettings] = lazy_nested(AgentSettings, "agent_settings")


@cache
def _get_main_settings() -> Settings:
    return Settings()


@cache
def get_settings(user_id: UserId | None) -> Settings:
    if user_id is None:
        return _get_main_settings()

    # per-user settings
    return _get_main_settings()


# noinspection PyArgumentList
primary_settings = Settings()
