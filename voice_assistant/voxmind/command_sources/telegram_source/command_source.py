import asyncio
import io

import ffmpeg
from loguru import logger
from speech_recognition import AudioData
from telegram import File, Update, Voice
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from voice_assistant.voxmind.app_interfaces.audio_recognizer import AudioRecognizer
from voice_assistant.voxmind.app_interfaces.command_source import CommandSource
from voice_assistant.voxmind.app_utils.settings import Settings


class TelegramBotCommandSource(CommandSource):
    def __init__(self, settings: Settings, sst_module: AudioRecognizer) -> None:
        self._token = settings.telegram_token
        self._chat_id = settings.telegram_chat_id
        self._bot = Application.builder().token(self._token).build()
        self._message_queue: asyncio.Queue[str] = asyncio.Queue()

        self._sst_module = sst_module

    async def get_command(self) -> str:
        return await self._message_queue.get()

    async def send_response(self, text: str) -> None:
        await self._bot.bot.send_message(chat_id=self._chat_id, text=text)
        logger.info(f"Answer sent to telegram: '{text}'")

    async def start(self) -> None:
        self._bot.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self._handle_text_message,
                block=False,
            )
        )
        self._bot.add_handler(
            MessageHandler(
                filters.VOICE,
                self._handle_voice_message,
                block=False,
            )
        )
        await self._bot.initialize()
        await self._bot.start()
        await self._bot.updater.start_polling()
        logger.info("Telegram bot started")

    async def _handle_text_message(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        message_text = update.message.text
        if not isinstance(message_text, str):
            raise ValueError(f"not suitable text: {message_text}")
        await self._message_queue.put(message_text)

    async def _handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        voice: Voice = update.message.voice
        file_id = voice.file_id
        duration = voice.duration

        logger.debug(f"Receive voice message duration {duration} seconds")

        voice_file: File = await context.bot.get_file(file_id)

        audio_data = await get_audiodata_from_file(voice_file)

        res = await self._sst_module.recognize_from_audiodata(audio_data)

        await self._message_queue.put(res)


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
