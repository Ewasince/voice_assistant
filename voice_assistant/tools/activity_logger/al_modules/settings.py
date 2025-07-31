from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings
from pytz import timezone
from pytz.tzinfo import BaseTzInfo


class ALSettings(BaseSettings):
    # calendar
    calendar_scopes: list[str] = ["https://www.googleapis.com/auth/calendar"]
    calendar_creds_file: Path = Path("data/credentials.json")
    calendar_token_file: Path = Path("data/token.json")
    calendar_id: str

    calendar_tz: BaseTzInfo = timezone("Europe/Moscow")

    # noinspection PyNestedDecorators
    @field_validator("calendar_tz", mode="before")
    @classmethod
    def parse_timezone(cls, v: Any) -> BaseTzInfo:
        if isinstance(v, BaseTzInfo):
            return v
        return timezone(v)
