from typing import Any, ClassVar

from pydantic import BaseModel, field_validator
from pydantic_settings import SettingsConfigDict
from pytz import timezone
from pytz.tzinfo import BaseTzInfo

from voice_assistant.app_utils.settings_utils.common import ExtendedConfigDict, HierarchicalSettings


class CalendarSettings(HierarchicalSettings):
    model_config = SettingsConfigDict(
        env_prefix="CALENDAR_",
    )

    tz: BaseTzInfo = timezone("Europe/Moscow")

    # noinspection PyNestedDecorators
    @field_validator("tz", mode="before")
    @classmethod
    def parse_timezone(cls, v: Any) -> BaseTzInfo:
        if isinstance(v, BaseTzInfo):
            return v
        return timezone(v)
