from __future__ import annotations

from functools import cache
from typing import ClassVar, Iterable

from voice_assistant.agent.settings import AgentSettings
from voice_assistant.app_utils.app_types import DEFAULT_USER_ID, UserId
from voice_assistant.app_utils.settings_utils.common import USERS_FIELD, HierarchicalSettings, lazy_nested
from voice_assistant.command_sources.enums import CommandSourcesTypes
from voice_assistant.command_sources.telegram_source.settings import TelegramSettings
from voice_assistant.services.calendar.settings import CalendarSettings
from voice_assistant.services.composio.settings import ComposioSettings
from voice_assistant.sst_modules.settings import SttSettings


class Settings(HierarchicalSettings):
    # database
    database_uri: str = "sqlite:///data/data.db"

    # recognizing settings
    key_phase: str = "помощник"
    regexp: str = r"[^A-Za-zА-ЯЁа-яё0-9 ]"
    language: str = "ru"

    # example recognizers settings
    use_gpu: bool = False
    whisper_model: str = "turbo"

    sources_to_use_list: tuple[CommandSourcesTypes, ...] = (CommandSourcesTypes.telegram,)
    active_users_list: tuple[UserId, ...] = (DEFAULT_USER_ID,)

    agent_settings: ClassVar[AgentSettings] = lazy_nested(AgentSettings)
    telegram_settings: ClassVar[TelegramSettings] = lazy_nested(TelegramSettings)
    calendar_settings: ClassVar[CalendarSettings] = lazy_nested(CalendarSettings)
    composio_settings: ClassVar[ComposioSettings] = lazy_nested(ComposioSettings)
    stt_settings: ClassVar[SttSettings] = lazy_nested(SttSettings)

    @property
    def users(self) -> Iterable[UserId]:
        return self._yaml_cache.get(USERS_FIELD, [])


@cache
def _get_main_settings() -> Settings:
    return Settings()


@cache
def get_settings(user_id: UserId | None = None) -> Settings:
    main_settings = _get_main_settings()
    if user_id is None:
        return main_settings

    # per-user settings
    return main_settings.merge(main_settings.get_nested_variables(USERS_FIELD, user_id))
