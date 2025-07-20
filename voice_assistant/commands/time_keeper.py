from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Final

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from loguru import logger

from voxmind.app_interfaces.command_performer import CommandPerformer
from voxmind.app_interfaces.llm_module import LLMClient
from voxmind.assistant_core.context import Context as GeneralContext

_ACTIVITY_END: Final[str] = "нет"
_ACTIVITY_NOT_END: Final[str] = "да"
_DEFINE_END_TASK_PROMPT: Final[str] = f"""\
Проанализируй следующее высказывание:

"{{sentence}}"

В этом предложении есть информация о том \
чем будет заниматься человек дальше \
или чем он занимается сейчас \
или какой деятельностью сейчас занят или будет занят \
или что привлекло его внимание сейчас или привлечёт \
? \
Ответь "{_ACTIVITY_END}" или "{_ACTIVITY_NOT_END}" без пояснений.\
"""

_DEFINE_TASK_TOPIC_PROMPT: Final[str] = """\
Прочитай следующее предложение:

"{sentence}"

Определи, о каком виде активности в нём идёт речь, и опиши эту активность несколькими словами, используя краткую, \
точную формулировку, без синонимов. Чем кратче тем лучше, в идеале одним словом. \
Не добавляй лишнего текста — только суть активности.
"""

SCOPES = ["https://www.googleapis.com/auth/calendar"]


@dataclass
class Contex:
    last_activity_topic: str | None = None
    last_activity_time: datetime | None = None


class CommandTimeKeeperGoogle(CommandPerformer):
    _command_topic: ClassVar[str] = "запись активности"
    _context_class_type: ClassVar[type] = Contex

    _define_end_task_prompt: ClassVar[str] = _DEFINE_END_TASK_PROMPT
    _define_task_topic_prompt: ClassVar[str] = _DEFINE_TASK_TOPIC_PROMPT

    def __init__(self, gpt_module: LLMClient):
        self._llm_module = gpt_module

        # Авторизация
        flow = InstalledAppFlow.from_client_secrets_file("../.cache/credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

        # Создание сервиса
        self._service = build("calendar", "v3", credentials=creds)

    async def perform_command(self, command_text: str, context: GeneralContext) -> str | None:
        activity_type = self._llm_module.get_simple_answer(self._generate_define_activity_end_prompt(command_text))
        logger.debug(f"Guessed activity event: is continue activity? {activity_type}.")
        # topic = self._llm_module.get_answer(self._generate_define_task_topic_prompt(text_context))

        command_context: Contex = self._get_reliable_context(context)

        if activity_type == _ACTIVITY_NOT_END:
            return await self._commit_new_activity(command_text, command_context)

        if activity_type != _ACTIVITY_END:
            logger.warning(f"Unknown activity type ({activity_type}): {command_text}")
            return await self._commit_new_activity(command_text, command_context)

        if command_context.last_activity_topic:
            return await self._commit_end_activity(command_context)

        logger.warning(f"Noticed end activity without last activity: {command_text}")
        return await self._commit_new_activity(command_text, command_context)

    async def _commit_new_activity(self, command_text: str, command_context: Contex) -> str:
        current_time = datetime.now()  # noqa: DTZ005

        response_message = ""

        last_activity_topic = command_context.last_activity_topic
        last_activity_time = command_context.last_activity_time
        if last_activity_topic and last_activity_time:
            await self._jot_down_activity(
                last_activity_topic,
                last_activity_time,
                current_time,
            )
            response_message += f'Записал активность "{last_activity_topic}". '

        new_activity_topic = self._llm_module.get_simple_answer(self._generate_define_task_topic_prompt(command_text))
        command_context.last_activity_topic = new_activity_topic
        command_context.last_activity_time = current_time

        response_message += f'Запомнил активность "{new_activity_topic}". '

        return response_message

    async def _commit_end_activity(self, command_context: Contex) -> str:
        current_time = datetime.now()  # noqa: DTZ005

        last_activity_topic = command_context.last_activity_topic
        last_activity_time = command_context.last_activity_time

        if last_activity_topic and last_activity_time:
            await self._jot_down_activity(
                last_activity_topic,
                last_activity_time,
                current_time,
            )
        else:
            logger.error(f"commit end activity called without last activity {command_context}")

        command_context.last_activity_topic = None
        command_context.last_activity_time = None

        return f'Записал конец активности "{last_activity_topic}"'

    async def _jot_down_activity(
        self,
        topic: str,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        logger.info(f"Бот записал активность {topic} с {start_time.strftime('%H:%M')} по {end_time.strftime('%H:%M')}")

        # Данные мероприятия
        event = {
            "summary": topic,
            # 'location': 'Москва, ул. Ленина, 1',
            # 'description': 'Обсудим проект.',
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "Europe/Moscow",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "Europe/Moscow",
            },
            # 'attendees': [
            #     {'email': 'example@gmail.com'},
            # ],
        }

        event = (
            self._service.events()
            .insert(
                calendarId="1390da56718a398ff28cdefb909fffc3aa55bc7aea60faafdbed20e5c9e2121a@group.calendar.google.com",
                body=event,
            )
            .execute()
        )
        print("Мероприятие создано: {}".format(event.get("htmlLink")))

    def _generate_define_activity_end_prompt(self, command: str) -> str:
        return self._define_end_task_prompt.format(
            sentence=command,
        )
        # logger.debug(f"prompt: \n\n{prompt}\n")

    def _generate_define_task_topic_prompt(self, command: str) -> str:
        return self._define_task_topic_prompt.format(
            sentence=command,
        )
