from abc import ABC, abstractmethod


class IGPTModule(ABC):

    @abstractmethod
    def get_answer(self, text: str) -> str:
        raise NotImplementedError
