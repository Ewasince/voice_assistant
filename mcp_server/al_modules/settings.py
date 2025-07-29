from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    # recognizing settings
    database_uri: str = "sqlite:///data.db"
