from abc import ABC, abstractmethod
from typing import Callable

from app_interfaces.i_command_performer import ICommandPerformer


class ICommandRecognizer(ABC):

    @abstractmethod
    def add_command(self, command_text: str, func: ICommandPerformer.perform_command):
        # FIXME: проверить как рабоатет
        raise NotImplementedError

    @abstractmethod
    def process_command(self, command_text: str):
        raise NotImplementedError
