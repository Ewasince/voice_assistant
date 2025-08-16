from async_lru import alru_cache

from voice_assistant.app_interfaces.source_factory import SourceFactory
from voice_assistant.command_sources.telegram_source.settings import telegram_settings
from voice_assistant.sst_modules.sst_modules_factory import get_sst_module


@alru_cache
async def get_telegram_bot() -> SourceFactory:
    from voice_assistant.command_sources.telegram_source.command_source import TelegramBot  # noqa: PLC0415

    audio_recognizer = get_sst_module() if telegram_settings.telegram_recognize_voice else None
    return TelegramBot(audio_recognizer)
