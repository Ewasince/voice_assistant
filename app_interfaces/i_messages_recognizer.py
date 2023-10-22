from abc import ABC, abstractmethod


class IMessagesRecognizer(ABC):
    """Определяет интерфейс класса, который выдаёт расшифрованный текст"""

    @abstractmethod
    def get_audio(self) -> str | None:
        """Вызывается для получения следующего текста с командами и возвращает его, когда таковой будет получен"""
        raise NotImplementedError
