from abc import ABC, abstractmethod


class LLMModule(ABC):
    @abstractmethod
    def get_answer(self, text: str) -> str:
        raise NotImplementedError
