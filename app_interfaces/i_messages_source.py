from abc import ABC, abstractmethod
from typing import Callable


class IMessagesSource:
    @abstractmethod
    def wait_command(self) -> str:
        raise NotImplementedError
