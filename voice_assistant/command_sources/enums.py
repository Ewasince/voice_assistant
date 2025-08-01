from enum import StrEnum


class CommandSourcesTypes(StrEnum):
    local_voice = "LOCAL_VOICE"
    telegram = "TELEGRAM"
    web = "WEB"
