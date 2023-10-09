from abc import ABC, abstractmethod
from typing import Callable


class ICommandPerformer(ABC):
    @abstractmethod
    def add_command(self, command_str: str, func: Callable[..., None]):
        raise NotImplementedError

    @abstractmethod
    def perform_command(self, str):
        raise NotImplementedError
