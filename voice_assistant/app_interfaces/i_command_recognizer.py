from abc import ABC, abstractmethod
from typing import final

from voice_assistant.app_interfaces.i_command_performer import ICommandPerformer


class ICommandRecognizer(ABC):
    """Определяет интерфейс класса, который определяет к какой теме принадлежит команда"""

    def __init__(self):
        self._command_dict: dict[str, ICommandPerformer] = {}
        self._default_command: ICommandPerformer | None = None

    def add_command(self, command_class: ICommandPerformer):
        """Добавляет команды для распознавания. Для задания команды по-умолчанию, нужно передать команду с текстом None"""
        topic = command_class.get_command_topic()
        if not topic:
            self._default_command = command_class
            return
        self._command_dict[topic] = command_class
        pass

    @abstractmethod
    async def process_command_from_dict(self, command_text: str) -> str | None:
        raise NotImplementedError

    @final
    async def process_command(self, command_text: str) -> str | None:
        res = self.process_command_from_dict(command_text)

        if res is None and self._default_command:
            res = await self._default_command.perform_command(command_text)

        return res
