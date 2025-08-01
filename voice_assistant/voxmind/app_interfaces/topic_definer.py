from abc import ABC, abstractmethod


class TopicDefiner(ABC):
    @abstractmethod
    async def choose_topic_from_list(self, topics: list[str], current_topic: str) -> str | None:
        """Определяет к какой теме больше всех относится угадываемая тема"""
        raise NotImplementedError
