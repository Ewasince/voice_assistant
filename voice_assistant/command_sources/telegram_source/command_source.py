from asyncio import Queue
from collections import namedtuple
from functools import cache
from typing import AsyncGenerator

from loguru import logger
from telegram import Chat, File, Message, Update, User, Voice
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from voice_assistant.app_interfaces.audio_recognizer import AudioRecognizer
from voice_assistant.app_interfaces.command_source import CommandSource
from voice_assistant.app_utils.types import UserId
from voice_assistant.command_sources.telegram_source.settings import telegram_settings
from voice_assistant.command_sources.telegram_source.utils import get_audiodata_from_file
from voice_assistant.sst_modules.sst_whisper import get_whisper_sst_module

UserResponse = namedtuple("UserResponse", ["message_text", "chat_id"])

type ResponseQuery = Queue[UserResponse]


class TelegramBotCommandSource(CommandSource):
    def __init__(
        self,
        user_id: UserId,
        message_queue: ResponseQuery,
        bot: Application,
    ) -> None:
        super().__init__(user_id)
        self.message_queue = message_queue
        self._bot = bot

    async def _user_bot_interaction(self) -> AsyncGenerator[str | None, str]:
        user_message_data = await self.message_queue.get()
        yield None  # first yield None
        response = yield user_message_data.message_text

        await self._bot.bot.send_message(chat_id=user_message_data.chat_id, text=response)
        logger.info(f"Answer for user '{self.user_id}' sent to telegram: '{response}'")

    async def get_command(self) -> str:
        raise NotImplementedError

    async def send_response(self, text: str) -> None:
        raise NotImplementedError


class TelegramBot:
    def __init__(self, sst_module: AudioRecognizer) -> None:
        self._sst_module = sst_module

        self._bot = Application.builder().token(telegram_settings.telegram_token).build()

        self._message_queues_by_users: dict[int, ResponseQuery] = {}

        self.started = False

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
        self.started = True
        logger.info("Telegram bot started")

    def get_source_for_user(self, user_id: UserId) -> TelegramBotCommandSource:
        message_queue: ResponseQuery = Queue()

        tg_user_id = telegram_settings.telegram_tg_users_to_ids_map[user_id]

        self._message_queues_by_users[tg_user_id] = message_queue

        return TelegramBotCommandSource(user_id, message_queue, self._bot)

    async def _handle_text_message(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        user_data = self._get_user_data(update)
        if user_data is None:
            return
        message, user, chat, message_queue = user_data

        message_text = message.text
        if message_text is None:
            return

        await message_queue.put(UserResponse(message_text, chat.id))

    async def _handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_data = self._get_user_data(update)
        if user_data is None:
            return
        message, user, chat, message_queue = user_data

        voice: Voice = message.voice  # type: ignore[assignment]
        file_id = voice.file_id
        duration = voice.duration

        logger.debug(f"Receive voice message duration {duration} seconds")

        voice_file: File = await context.bot.get_file(file_id)

        audio_data = await get_audiodata_from_file(voice_file)

        message_text = await self._sst_module.recognize_from_audiodata(audio_data)

        await message_queue.put(UserResponse(message_text, chat.id))

    def _get_user_data(self, update: Update) -> tuple[Message, User, Chat, ResponseQuery] | None:
        message = update.message
        if message is None:
            return None

        from_user = message.from_user
        if from_user is None:
            return None

        chat = message.chat
        if chat is None:
            return None

        tg_user_id = from_user.id
        tg_user_name = from_user.username

        message_queue = self._message_queues_by_users.get(tg_user_id)
        if message_queue is None:
            logger.info(f"Bot has message from unknown tg user {tg_user_name} ({tg_user_id}): {message.text}")
            return None

        return message, from_user, chat, message_queue


@cache
def get_telegram_bot() -> TelegramBot:
    audio_recognizer = get_whisper_sst_module()
    return TelegramBot(audio_recognizer)


async def get_tg_source(user_id: UserId) -> CommandSource:
    telegram_bot = get_telegram_bot()

    command_source = telegram_bot.get_source_for_user(user_id)

    if not telegram_bot.started:
        await telegram_bot.start()

    return command_source
