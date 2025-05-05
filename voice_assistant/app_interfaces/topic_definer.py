from abc import ABC, abstractmethod


class ITopicDefiner(ABC):
    @abstractmethod
    async def define_topic(self, topics: list[str], current_topic: str) -> str | None:
        """Определяет к какой теме больше всех относится угадываемая тема"""
        raise NotImplementedError
