from abc import ABC, abstractmethod
from typing import Self


class CommandIterator(ABC):
    async def __aiter__(self) -> Self:
        return self

    @abstractmethod
    async def __anext__(self) -> str:
        raise NotImplementedError



class TextSource(ABC):
    """Определяет интерфейс класса, который выдаёт расшифрованный текст"""

    @abstractmethod
    async def next_text_command(self) -> str | None:
        """
        Выдаёт текст сообщенмия и блокирует данный
        контекст исполнения пока не выдаст текст расшифрованного сообщения
        """
        raise NotImplementedError
