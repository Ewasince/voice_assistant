import asyncio
from queue import Queue
from threading import Thread

from loguru import logger
from speech_recognition import AudioData, Microphone, Recognizer

from voice_assistant.voxmind.app_interfaces.audio_recognizer import AudioRecognizer
from voice_assistant.voxmind.app_utils.utils import Settings


class MicrophoneListener:
    def __init__(
        self,
        settings: Settings,
        sst_module: AudioRecognizer,
        *,
        do_setup_micro: bool = True,
    ):
        self._recognizer: Recognizer = Recognizer()
        self._microphone: Microphone = Microphone()
        self._settings = settings

        self._sst_module = sst_module

        self._setup_microphone(do_setup_micro)

        self._audio_queue: Queue[AudioData] = Queue()
        self._result_queue: Queue[str] = Queue()
        self._stop_listening = None
        self._listen_thread: Thread | None = None

    async def next_utterance(self) -> str | None:
        return await asyncio.to_thread(self._next_utterance)

    def _next_utterance(self) -> str | None:
        return self._result_queue.get()

    def start_listen(self) -> None:
        logger.info("start listening!")

        if self._stop_listening is not None:
            return
        self._stop_listening = self._recognizer.listen_in_background(self._microphone, self._audio_callback)
        self._listen_thread = Thread(target=asyncio.run, args=(self._process_audio_loop(),), daemon=True)
        self._listen_thread.start()

    def stop_listen(self) -> None:
        if not self._stop_listening:
            return
        self._stop_listening(wait_for_stop=False)
        self._stop_listening = None

    def _audio_callback(self, audio: AudioData) -> None:
        self._audio_queue.put(audio)
        logger.info(f"audio queue size +1 ={self._audio_queue.qsize()}")

    async def _process_audio_loop(self) -> None:
        while self._stop_listening is not None:
            logger.info(f"audio queue size -1 ={self._audio_queue.qsize()}")
            audio = self._audio_queue.get()
            await self._recognize_and_enqueue(audio)

    async def _recognize_and_enqueue(self, audio: AudioData) -> None:
        result = await self._sst_module.recognize_from_audiodata(audio)
        logger.info(f"recognize result = {result}")
        self._result_queue.put(result)

    def _setup_microphone(self, do_setup_micro: bool) -> None:
        if not do_setup_micro:
            return

        print("Момент тишины, микрофон настраивается...")
        with self._microphone as source:
            self._recognizer.adjust_for_ambient_noise(source)

        print("Микрофон настроен!")
