from abc import ABC, abstractmethod

from loguru import logger
from speech_recognition import AudioData


class AudioRecognizer(ABC):
    def __init__(self) -> None:
        self._logger = logger.bind(action="STT")

    @abstractmethod
    async def recognize_from_audiodata(self, audio_data: AudioData) -> str:
        pass
