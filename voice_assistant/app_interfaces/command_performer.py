from abc import ABC, abstractmethod
from typing import ClassVar


class CommandPerformer(ABC):
    """Определяет класс, содержащий в себе команду"""

    # command topic defines how llm will see this command
    _command_topic: ClassVar[str] = ""

    @property
    def command_topic(self) -> str:
        if self._command_topic is None:
            msg = f"command topic not set for {self.__class__.__name__}"
            raise ValueError(msg)

        return self._command_topic

    @abstractmethod
    async def perform_command(self, command_text: str) -> str | None:
        """Метод выполняющий команду. Может менять своё поведение, в зависимости от переданного контекста.
        Возвращает текст и/или делает какие-либо изменения в системе.
        """
        raise NotImplementedError
