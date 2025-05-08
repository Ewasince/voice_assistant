import os
import wave
from datetime import datetime

import pyaudio
import typing_extensions

from voice_assistant.app_utils.settings import Settings


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
