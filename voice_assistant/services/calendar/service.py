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

        self._logger = logger.bind(user_id=user_id, action="calendar")

    async def commit_new_activity(
        self,
        activity_topic: str,
        command_context: Contex,
    ) -> str:
        response_message = ""
        try:
            current_time = datetime.now(tz=calendar_settings.calendar_tz)

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

            # response = f"я записал, что начал активность '{new_activity}'"
            #
            # if new_activity_offset:
            #     dt_offset = datetime.strptime(new_activity_offset, "%H:%M:%S")
            #     delta = timedelta(hours=dt_offset.hour, minutes=dt_offset.minute, seconds=dt_offset.second)
            #     delta_minutes = delta.seconds / 60
            #     response += f" {delta_minutes:.2f} минут назад"
        except Exception as e:
            response_message += f"Возникла ошибка: {e}"

        return f"Передай пользователю — {response_message}"

    async def commit_end_activity(
        self,
        command_context: Contex,
    ) -> str:
        response_message = ""
        try:
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
                self._logger.error(f"commit end activity called without last activity {command_context}")

            command_context.last_activity_topic = None
            command_context.last_activity_time = None

            if last_activity_topic:
                response_message += f'Записал конец активности "{last_activity_topic}"'
            else:
                response_message += "Не было информации о последней активности"

            # response = "я записал, что закончил активность"
            #
            # dt_offset = datetime.strptime(end_activity_offset or "00:00:00", "%H:%M:%S")
            # delta = timedelta(hours=dt_offset.hour, minutes=dt_offset.minute, seconds=dt_offset.second)
            # delta_minutes = delta.seconds / 60
            #
            # if delta_minutes:
            #     response += f" {delta_minutes:.2f} минут назад"
        except Exception as e:
            response_message += f"Возникла ошибка: {e}"

        return f"Передай пользователю — {response_message}"

    async def _jot_down_activity(
        self,
        topic: str,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        self._logger.info(
            f"write activity '{topic}' from {start_time.strftime('%H:%M:%S')} по {end_time.strftime('%H:%M:%S')}"
        )

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
        self._logger.debug("event created: {}".format(event.get("htmlLink")))
