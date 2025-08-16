from functools import cache

from loguru import logger

from voice_assistant.app_interfaces.audio_recognizer import AudioRecognizer
from voice_assistant.sst_modules.settings import stt_settings

logger = logger.bind(action="LOAD_STT")


@cache
def get_sst_module() -> AudioRecognizer:
    if stt_settings.stt_mode == "api":
        return _get_api_sst_module()
    if stt_settings.stt_mode == "local":
        return _get_whisper_sst_module()
    raise ValueError("stt_mode must be 'local' or 'api'")


@cache
def _get_whisper_sst_module() -> AudioRecognizer:
    from voice_assistant.sst_modules.sst_whisper import WhisperSST  # noqa: PLC0415

    logger.info("getting local whisper stt module")
    return WhisperSST()


@cache
def _get_api_sst_module() -> AudioRecognizer:
    from voice_assistant.sst_modules.api_sst import OpenAIAPISST  # noqa: PLC0415

    logger.info("getting api stt module")
    return OpenAIAPISST()
