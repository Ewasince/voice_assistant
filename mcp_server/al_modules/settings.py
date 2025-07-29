from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import field_validator
from pydantic_settings import BaseSettings


class ALSettings(BaseSettings):
    # database
    database_uri: str = "sqlite:///data.db"

    # calendar
    calendar_scopes: list[str] = ["https://www.googleapis.com/auth/calendar"]
    calendar_creds_file: Path = Path("creds/credentials.json")
    calendar_token_file: Path = Path("creds/token.json")
    calendar_id: str

    calendar_tz: ZoneInfo = ZoneInfo("Europe/Moscow")

    # noinspection PyNestedDecorators
    @field_validator("calendar_tz", mode="before")
    @classmethod
    def parse_timezone(cls, v):
        if isinstance(v, ZoneInfo):
            return v
        return ZoneInfo(v)
