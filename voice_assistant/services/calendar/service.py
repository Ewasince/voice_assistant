from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from loguru import logger

from voice_assistant.app_utils.types import UserId
from voice_assistant.database.models import Contex
from voice_assistant.services.calendar.settings import calendar_settings


class CalendarService:
    def __init__(self, user_id: UserId, creds: Credentials, calendar_id: str) -> None:
        self._user_id = user_id
        self._calendar_id = calendar_id
        self._calendar_service = build("calendar", "v3", credentials=creds)

    async def commit_new_activity(
        self,
        activity_topic: str,
        command_context: Contex,
    ) -> str:
        current_time = datetime.now(tz=calendar_settings.calendar_tz)

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

        command_context.last_activity_topic = activity_topic
        command_context.last_activity_time = current_time

        response_message += f'Запомнил активность "{activity_topic}". '

        return response_message

    async def commit_end_activity(
        self,
        command_context: Contex,
    ) -> str:
        current_time = datetime.now(tz=calendar_settings.calendar_tz)

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

        if last_activity_topic:
            return f'Записал конец активности "{last_activity_topic}"'

        return "Не было информации о последней активности"

    async def _jot_down_activity(
        self,
        topic: str,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        logger.info(f"бот записал активность {topic} с {start_time.strftime('%H:%M')} по {end_time.strftime('%H:%M')}")

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
            self._calendar_service.events()
            .insert(
                calendarId=self._calendar_id,
                body=event,
            )
            .execute()
        )
        logger.info("event created: {}".format(event.get("htmlLink")))
