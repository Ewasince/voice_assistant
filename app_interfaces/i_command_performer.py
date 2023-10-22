from abc import ABC, abstractmethod


class ICommandPerformer(ABC):
    """Определяет класс, содержащий в себе команду"""

    @abstractmethod
    def get_command_topic(self) -> str:
        """Возвращает текст, при котором должна вызываться команда."""
        raise NotImplementedError

    @abstractmethod
    def perform_command(self, command_context: str) -> str | None:
        """Метод выполняющий команду. Может менять своё поведение, в зависимости от переданного контекста.
        Возвращает текст и/или делает какие-либо изменения в системе.
        """
        raise NotImplementedError
