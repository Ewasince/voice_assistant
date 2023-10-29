from abc import ABC, abstractmethod

from voice_assistant.app_interfaces.i_command_performer import ICommandPerformer


class ICommandRecognizer(ABC):
    """Определяет интерфейс класса, который определяет к какой теме принадлежит команда"""

    def __init__(self):
        self._command_dict: dict[str, ICommandPerformer] = {}

    def add_command(self, command_class: ICommandPerformer):
        self._command_dict[command_class.get_command_topic()] = command_class
        pass

    @abstractmethod
    async def process_command(self, command_text: str) -> str | None:
        raise NotImplementedError
