import os
import wave
from datetime import datetime
import typing_extensions

import pyaudio
import speech_recognition as sr

from messages_local_mic.config import config
from messages_local_mic.interfaces.i_messages_recognizer import IMessagesRecognizer


class AudioRecognizer(IMessagesRecognizer):
    def __init__(self):
        self.r = sr.Recognizer()
        self.m = sr.Microphone()

        self.setup_microphone()
        pass

    def setup_microphone(self):
        print("Момент тишины, микрофон настраивается...")
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)

        # print(f"{self.r.energy_threshold}") # self.r.energy_threshold
        print("Микрофон настроен!")
        return

    def get_audio(self) -> str | None:
        print("Слушаю...")
        with self.m as source:
            audio = self.r.listen(source)
        # print("Got it! Now to recognize it...")
        text = self.recognize_speech(audio)
        return text

    def recognize_from_file(self, audio_filename: str) -> str:
        # Загружаем аудио файл
        audio_file = sr.AudioFile(audio_filename)

        with audio_file as source:
            audio_data = self.r.record(source)
            text = self.recognize_speech(audio_data)

        return text

    def recognize_speech(self, audio_data: sr.AudioData) -> str | None:
        # Распознаем речь из аудио
        try:
            # recognize speech using Google Speech Recognition
            value = self.r.recognize_google(audio_data, language=config.language)

            # print("You said {}".format(value))
        except sr.UnknownValueError:
            # print("Oops! Didn't catch that")
            return None
        except sr.RequestError as e:
            print(
                f"Couldn't request results from Google Speech Recognition service; {e}"
            )
            raise e
        else:
            return value


@typing_extensions.deprecated("The `get_waw` is deprecated")
def get_waw(seconds=3) -> str:
    try:
        # tmpdirname = tempfile.TemporaryDirectory(dir=temp_dir)
        # print('created temporary directory', tmpdirname)
        # filename = os.path.join(tmpdirname, str(time.time()), '.waw')

        filename = os.path.join(config.data_dir, str(datetime.now()) + ".wav")
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
        for i in range(0, int(config.rate / config.chunk * seconds)):
            data = stream.read(config.chunk)
            frames.append(data)

        # Остановить и закрыть поток
        stream.stop_stream()
        stream.close()
        # Завершить интерфейс PortAudio
        p.terminate()

        print("Finished recording!")

        # Сохранить записанные данные в виде файла WAV
        wf = wave.open(filename, "wb")
        wf.setnchannels(config.channels)
        wf.setsampwidth(p.get_sample_size(config.sample_format))
        wf.setframerate(config.rate)
        wf.writeframes(b"".join(frames))
        wf.close()

        return filename
    except Exception as e:
        raise e
    finally:
        pass
