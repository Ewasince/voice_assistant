import io

import ffmpeg
from speech_recognition import AudioData
from telegram import File


async def get_audiodata_from_file(voice_file: File) -> AudioData:
    # Скачиваем voice в память
    ogg_io = io.BytesIO()
    await voice_file.download_to_memory(out=ogg_io)
    ogg_io.seek(0)

    # Конвертируем OGG/Opus в WAV PCM (16-bit signed, 16kHz, mono)
    wav_bytes, _ = (
        ffmpeg.input("pipe:0")
        .output("pipe:1", format="wav", ac=1, ar=16000, acodec="pcm_s16le")
        .run(input=ogg_io.read(), capture_stdout=True, capture_stderr=True)
    )

    # Создаем AudioData из WAV-данных
    return AudioData(wav_bytes, sample_rate=16000, sample_width=2)
