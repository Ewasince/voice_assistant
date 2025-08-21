from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import SettingsConfigDict

from voice_assistant.app_utils.settings_utils.common import HierarchicalSettings


class LogsSettings(HierarchicalSettings):
    model_config = SettingsConfigDict(
        env_prefix="LOG_",
    )
    level: str = "INFO"
    file: str = "data/logs.log"
    rotation: str | None = "20 MB"
    retention: int | None = 5
    compression: str | None = "zip"

    # noinspection PyNestedDecorators
    @field_validator("level", mode="before")
    @classmethod
    def parse_timezone(cls, v: str) -> str:
        return v.upper()
