import asyncio

from loguru import logger
from telegram import File, Update, Voice
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from voice_assistant.app_interfaces.audio_recognizer import AudioRecognizer
from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.settings import primary_settings
from voice_assistant.app_utils.types import UserId
from voice_assistant.command_sources.telegram_source.utils import get_audiodata_from_file
from voice_assistant.sst_modules.sst_whisper import _get_whisper_sst_module


class TelegramBotCommandSource(CommandSource):
    def __init__(self, user_id: UserId, sst_module: AudioRecognizer) -> None:
        super().__init__(user_id)
        self._token = primary_settings.telegram_token
        self._chat_id = primary_settings.telegram_chat_id
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
        await self._bot.updater.start_polling()  # type: ignore[union-attr]
        logger.info("Telegram bot started")

    async def _handle_text_message(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        message_text = update.message.text  # type: ignore[union-attr]
        if not isinstance(message_text, str):
            raise ValueError(f"not suitable text: {message_text}")
        await self._message_queue.put(message_text)

    async def _handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        voice: Voice = update.message.voice  # type: ignore[union-attr, assignment]
        file_id = voice.file_id
        duration = voice.duration

        logger.debug(f"Receive voice message duration {duration} seconds")

        voice_file: File = await context.bot.get_file(file_id)

        audio_data = await get_audiodata_from_file(voice_file)

        res = await self._sst_module.recognize_from_audiodata(audio_data)

        await self._message_queue.put(res)


async def get_tg_source(user_id: UserId) -> CommandSource:
    audio_recognizer = _get_whisper_sst_module()
    command_source = TelegramBotCommandSource(user_id, audio_recognizer)
    await command_source.start()

    return command_source
