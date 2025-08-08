from pydantic import Field

from voice_assistant.app_utils.app_types import UserId
from voice_assistant.app_utils.base_settings import ExtendedSettings


class TelegramSettings(ExtendedSettings):
    telegram_token: str = ""
    telegram_chat_id: int = 0
    telegram_recognize_voice: bool = True

    telegram_tg_users_to_ids_map: dict[int, UserId] = Field(default_factory=dict)


telegram_settings = TelegramSettings()
