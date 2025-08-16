from abc import ABC, abstractmethod


class UserAgent(ABC):
    @abstractmethod
    async def run_agent(self, input_text: str) -> str | None:
        pass
