from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def get_simple_answer(self, text: str) -> str:
        raise NotImplementedError
