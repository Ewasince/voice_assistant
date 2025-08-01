import io

import numpy as np
import soundfile as sf
import whisper
from loguru import logger
from speech_recognition import AudioData, RequestError, UnknownValueError

from voice_assistant.voxmind.app_interfaces.audio_recognizer import AudioRecognizer
from voice_assistant.voxmind.app_utils.utils import Settings


class WhisperSST(AudioRecognizer):
    def __init__(self, settings: Settings):
        self._settings = settings
        self._setup_whisper()

    def _setup_whisper(self) -> None:
        self._whisper_model = whisper.load_model(self._settings.whisper_model)

        logger.info("Initialized whisper model")

        if self._settings.use_gpu:
            import torch

            logger.info(f"Cuda available: {torch.cuda.is_available()}")

    async def recognize_from_audiodata(self, audio_data: AudioData) -> str:
        try:
            wav_bytes = audio_data.get_wav_data(convert_rate=16000)
            wav_stream = io.BytesIO(wav_bytes)
            audio_array, sampling_rate = sf.read(wav_stream)
            audio_array = audio_array.astype(np.float32)

            result = self._whisper_model.transcribe(audio_array, language="ru")
            value = result["text"]
        except UnknownValueError:
            logger.error("Cant recognize")
            return ""
        except RequestError as e:
            logger.error(f"Couldn't request results from Google Speech Recognition service; {e}")
            raise e
        else:
            return value
