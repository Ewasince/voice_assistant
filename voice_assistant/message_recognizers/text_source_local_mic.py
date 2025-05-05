import os
import wave
from datetime import datetime

import pyaudio
import speech_recognition as sr
import typing_extensions

from voice_assistant.app_interfaces.message_recognizer import TextSource
from voice_assistant.app_utils.settings import Settings


class TextSourceLocalMic(TextSource):
    # TODO: разделить класс на распознаватель и источник аудио
    def __init__(self, setup_micro=True):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.config = Settings()

        if setup_micro:
            self.setup_microphone()

    def setup_microphone(self):
        print("Момент тишины, микрофон настраивается...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # print(f"{self.recognizer.energy_threshold}") # self.recognizer.energy_threshold
        print("Микрофон настроен!")

    async def next_text_command(self) -> str | None:
        print("Слушаю...")
        with self.microphone as source:
            audio = self.recognizer.listen(source)
        # print("Got it! Now to recognize it...")
        return self.recognize_speech(audio)

    def recognize_speech(self, audio_data: sr.AudioData) -> str | None:
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

    def recognize_from_file(self, audio_filename: str) -> str:
        # Загружаем аудио файл
        audio_file = sr.AudioFile(audio_filename)

        with audio_file as source:
            audio_data = self.recognizer.record(source)
            return self.recognize_speech(audio_data)



@typing_extensions.deprecated("The `get_waw` is deprecated")
def _get_waw(seconds=3) -> str:
    config = Settings()

    try:
        # tmpdirname = tempfile.TemporaryDirectory(dir=temp_dir)
        # print('created temporary directory', tmpdirname)
        # filename = os.path.join(tmpdirname, str(time.time()), '.waw')

        filename = os.path.join(config.data_dir, str(datetime.now()) + ".wav")  # noqa: DTZ005
        filename = filename.replace(":", ";")
        p = pyaudio.PyAudio()  # Создать интерфейс для PortAudio

        print(f"Recording ({seconds} seconds...")

        stream = p.open(
            format=config.sample_format,
            channels=config.channels,
            rate=config.rate,
            frames_per_buffer=config.chunk,
            input_device_index=1,  # индекс устройства с которого будет идти запись звука
            input=True,
        )

        frames = []  # Инициализировать массив для хранения кадров

        # Хранить данные в блоках в течение 3 секунд
        for _i in range(int(config.rate / config.chunk * seconds)):
            data = stream.read(config.chunk)
            frames.append(data)

        # Остановить и закрыть поток
        stream.stop_stream()
        stream.close()
        # Завершить интерфейс PortAudio
        p.terminate()

        print("Finished recording!")

        # Сохранить записанные данные в виде файла WAV
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(config.channels)
            wf.setsampwidth(p.get_sample_size(config.sample_format))
            wf.setframerate(config.rate)
            wf.writeframes(b"".join(frames))

        return filename
    except Exception as e:
        raise e
    finally:
        pass
