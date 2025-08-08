from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from loguru import logger

from voice_assistant.app_utils.app_types import UserId


class CalendarService:
    def __init__(self, user_id: UserId, creds: Credentials, calendar_id: str) -> None:
        self._user_id = user_id
        self._calendar_id = calendar_id
        self._calendar_service = build("calendar", "v3", credentials=creds)

        self._logger = logger.bind(user_id=user_id, action="calendar")

    async def jot_down_activity(
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
