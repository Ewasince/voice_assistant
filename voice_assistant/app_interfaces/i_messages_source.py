from abc import ABC, abstractmethod


class IMessagesSource(ABC):
    """Определяет интерфейс класса, который выдаёт нормализованный текст, содержащий команду"""

    @abstractmethod
    def wait_command(self) -> str:
        """Вызывается для получения следующего текста с командами и возвращает его, когда таковой будет получен"""
        raise NotImplementedError
