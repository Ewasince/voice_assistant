from abc import ABC, abstractmethod
from typing import Callable


class ICommandPerformer(ABC):

    @abstractmethod
    def perform_command(self, command_text: str):
        raise NotImplementedError
