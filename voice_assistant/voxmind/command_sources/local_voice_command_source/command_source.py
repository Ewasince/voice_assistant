import warnings

from loguru import logger
from plyer import notification

from voice_assistant.voxmind.app_interfaces.audio_recognizer import AudioRecognizer
from voice_assistant.voxmind.app_interfaces.command_source import CommandSource
from voice_assistant.voxmind.app_utils.utils import Settings, normalize_text
from voice_assistant.voxmind.command_sources.local_voice_command_source.microphone_listener import MicrophoneListener

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU*")


class LocalVoiceCommandSource(CommandSource):
    def __init__(self, settings: Settings, sst_module: AudioRecognizer, *, setup_micro: bool = True):
        self.config = settings

        self._listener = MicrophoneListener(settings, sst_module, do_setup_micro=setup_micro)
        self._listener.start_listen()
        logger.info("TTS initialized")

    async def get_command(self) -> str:
        logger.info("Listening...")
        while True:
            text = await self._listener.next_utterance()

            command = self._check_command_after_key_word(text)

            if command is not None:
                break

        return command

    async def send_response(self, text: str) -> None:
        notification.notify(
            title="Ответ Ассистента",
            message=text,
            app_name="Голосовой помощник",
            timeout=10,  # в секундах
        )

    def _check_command_after_key_word(self, input_text: str | None) -> str | None:
        if input_text is None:
            return None

        text = normalize_text(input_text)

        filtered_text = extract_text_after_command(text, self.config.key_phase)

        if not filtered_text:
            return None

        return filtered_text


def extract_text_after_command(text: str, key: str | None) -> str | None:
    if not key:
        return text.strip()

    pos = text.find(key)
    if pos == -1:
        return None

    pos = pos + len(key) + 1

    filtered_text = text[pos:]

    return filtered_text.strip()
