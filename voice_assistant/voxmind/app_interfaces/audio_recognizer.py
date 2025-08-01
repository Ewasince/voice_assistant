from abc import ABC, abstractmethod

from speech_recognition import AudioData


class AudioRecognizer(ABC):
    @abstractmethod
    async def recognize_from_audiodata(self, audio_data: AudioData) -> str:
        pass
