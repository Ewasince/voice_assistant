from async_lru import alru_cache

from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_interfaces.source_factory import SourceFactory
from voice_assistant.app_utils.app_types import UserId
from voice_assistant.command_sources.telegram_source.settings import telegram_settings
from voice_assistant.sst_modules.factory import get_sst_module


@alru_cache
async def get_telegram_bot() -> SourceFactory:
    from voice_assistant.command_sources.telegram_source.command_source import TelegramBot  # noqa: PLC0415

    audio_recognizer = get_sst_module() if telegram_settings.telegram_recognize_voice else None
    return TelegramBot(audio_recognizer)


@alru_cache
async def get_tg_source(user_id: UserId) -> CommandSource:
    from voice_assistant.command_sources.telegram_source.factory import get_telegram_bot  # noqa: PLC0415

    telegram_bot = await get_telegram_bot()

    return telegram_bot.get_source_for_user(user_id)
