from abc import ABC, abstractmethod

from app_interfaces.i_command_performer import ICommandPerformer


class ICommandRecognizer(ABC):
    """Определяет интерфейс класса, который определяет к какой теме принадлежит команда"""

    @abstractmethod
    def add_command(self, command_class: ICommandPerformer):
        raise NotImplementedError

    @abstractmethod
    def process_command(self, command_text: str) -> str | None:
        raise NotImplementedError
