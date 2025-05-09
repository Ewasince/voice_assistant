import speech_recognition as sr

from voice_assistant.app_utils.settings import Settings


class STTModule:
    def __init__(self, settings: Settings, *, setup_micro: bool = True):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.config = settings

        if setup_micro:
            self._setup_microphone()

    async def next_utterance(self) -> str | None:
        print("Слушаю...")
        with self.microphone as source:
            audio = self.recognizer.listen(source)
        # print("Got it! Now to recognize it...")
        return self._recognize_speech(audio)

    def _setup_microphone(self) -> None:
        print("Момент тишины, микрофон настраивается...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # print(f"{self.recognizer.energy_threshold}") # self.recognizer.energy_threshold
        print("Микрофон настроен!")

    def _recognize_speech(self, audio_data: sr.AudioData) -> str | None:
        # Распознаем речь из аудио
        try:
            # recognize speech using Google Speech Recognition
            value = self.recognizer.recognize_google(audio_data, language=self.config.language)

            # print("You said {}".format(value))
        except sr.UnknownValueError:
            # print("Oops! Didn't catch that")
            return None
        except sr.RequestError as e:
            print(f"Couldn't request results from Google Speech Recognition service; {e}")
            raise e
        else:
            return value

    def recognize_from_file(self, audio_filename: str) -> str | None:
        # Загружаем аудио файл
        audio_file = sr.AudioFile(audio_filename)

        with audio_file as source:
            audio_data = self.recognizer.record(source)
            return self._recognize_speech(audio_data)
