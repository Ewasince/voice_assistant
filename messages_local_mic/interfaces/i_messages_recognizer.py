from abc import ABC, abstractmethod


class IMessagesRecognizer(ABC):

    @abstractmethod
    def get_audio(self) -> str:
        raise NotImplementedError
