from loguru import logger

from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.settings import primary_settings
from voice_assistant.command_sources.enums import CommandSourcesTypes
from voice_assistant.command_sources.local_voice_command_source.command_source import get_local_source
from voice_assistant.command_sources.telegram_source.command_source import get_tg_source
from voice_assistant.command_sources.web_voice_command_source.command_source import get_web_source


async def get_sources() -> list[CommandSource]:
    sources_types: list[CommandSourcesTypes] = primary_settings.sources_to_use_list
    logger.info(f"Initializing command sources: {', '.join(sources_types)}")

    sources: list[CommandSource] = []
    if CommandSourcesTypes.local_voice in sources_types:
        sources.append(get_local_source())
    if CommandSourcesTypes.telegram in sources_types:
        sources.append(await get_tg_source())
    if CommandSourcesTypes.web in sources_types:
        sources.append(get_web_source())

    return sources
