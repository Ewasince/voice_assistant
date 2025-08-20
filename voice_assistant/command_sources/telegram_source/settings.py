from typing import ClassVar

from pydantic import BaseModel

from voice_assistant.app_utils.base_settings import ExtendedConfigDict


class TelegramSettings(BaseModel):
    model_config: ClassVar[ExtendedConfigDict] = {
        "env_prefix": "TELEGRAM_",
        "extra": "ignore",
    }
    token: str = ""
    recognize_voice: bool = True

    tg_user_ids: list[int] = []
