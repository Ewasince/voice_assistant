from pydantic_settings import SettingsConfigDict

from voice_assistant.app_utils.settings_utils.common import HierarchicalSettings


class TelegramSettings(HierarchicalSettings):
    model_config = SettingsConfigDict(
        env_prefix="TELEGRAM_",
    )
    token: str = ""
    recognize_voice: bool = True

    tg_user_ids: list[int] = []
