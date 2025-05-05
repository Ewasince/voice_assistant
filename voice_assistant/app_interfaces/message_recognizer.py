from abc import ABC, abstractmethod


class TextSource(ABC):
    """Определяет интерфейс класса, который выдаёт расшифрованный текст"""

    @abstractmethod
    async def next_text_command(self) -> str | None:
        """
        Выдаёт текст сообщенмия и блокирует данный
        контекст исполнения пока не выдаст текст расшифрованного сообщения
        """
        raise NotImplementedError
