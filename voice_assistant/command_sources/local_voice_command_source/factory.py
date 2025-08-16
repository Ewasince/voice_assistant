from functools import cache

from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.app_types import DEFAULT_USER_ID
from voice_assistant.sst_modules.factory import get_sst_module


@cache
def get_local_source() -> CommandSource:
    from voice_assistant.command_sources.local_voice_command_source.command_source import (  # noqa: PLC0415
        LocalVoiceCommandSource,
    )

    audio_recognizer = get_sst_module()
    command_source: CommandSource = LocalVoiceCommandSource(DEFAULT_USER_ID, audio_recognizer)
    return command_source
