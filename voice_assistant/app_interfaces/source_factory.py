from abc import ABC, abstractmethod

from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.app_types import UserId


class SourceFactory(ABC):
    @abstractmethod
    def get_source_for_user(self, user_id: UserId) -> CommandSource:
        pass
