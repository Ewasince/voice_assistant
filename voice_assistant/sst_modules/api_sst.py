import openai
from loguru import logger
from openai import AsyncOpenAI
from speech_recognition import AudioData, RequestError, UnknownValueError

from voice_assistant.app_interfaces.audio_recognizer import AudioRecognizer
from voice_assistant.app_utils.settings import get_settings


class OpenAIAPISST(AudioRecognizer):
    def __init__(self) -> None:
        super().__init__()
        stt_settings = get_settings().stt_settings
        self.client = AsyncOpenAI(api_key=stt_settings.api_key.get_secret_value(), base_url=stt_settings.base_url)
        self.model = stt_settings.model
        self.language = stt_settings.language

        # logger.info(f"Initialized OpenAI SDK STT (model={self.model})")

    async def recognize_from_audiodata(self, audio_data: AudioData) -> str:
        wav_bytes: bytes = audio_data.get_wav_data(convert_rate=16000)
        try:
            resp = await self.client.audio.transcriptions.create(
                model=self.model,
                response_format="json",
                file=("audio.wav", wav_bytes, "audio/wav"),
                language=self.language,
            )
            text = (resp.text or "").strip()
            if not text:
                raise UnknownValueError()
            return text
        except UnknownValueError:
            logger.error("Не удалось распознать речь (пустой результат).")
            return ""
        except openai.APIError as e:
            logger.error(f"STT API error: {e}")
            raise RequestError(str(e)) from e
