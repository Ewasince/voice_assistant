from abc import ABC, abstractmethod


class IMessagesRecognizer(ABC):
    """Определяет интерфейс класса, который выдаёт расшифрованный текст"""

    @abstractmethod
    async def get_audio(self) -> str | None:
        """Выдаёт текст сообщенмия и блокирует данный контекст исполнения пока не выдаст текст расшифрованного сообщения"""
        raise NotImplementedError
