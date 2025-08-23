from datetime import datetime

from composio import Composio
from loguru import logger

from voice_assistant.app_utils.app_types import UserId


class CalendarService:
    def __init__(
        self,
        user_id: UserId,
        calendar_id: str,
        composio: Composio,
    ) -> None:
        self._user_id = user_id
        self._calendar_id = calendar_id
        self._composio = composio

        self._logger = logger.bind(user_id=user_id, action="calendar")

    async def jot_down_activity(
        self,
        topic: str,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        self._logger.info(
            f"write activity '{topic}' "
            f"from {start_time.strftime('%d.%m.%y %H:%M:%S %Z %z')} "
            f"to {end_time.strftime('%d.%m.%y %H:%M:%S %Z %z')}"
        )

        if int(end_time.strftime("%y%m%d")) != int(start_time.strftime("%y%m%d")):
            # if end activity on next day — cut
            end_time = start_time.replace(hour=23, minute=59, second=59)

            self._logger.debug(f"activity dates doesn't match, cut end time {end_time.strftime('%H:%M:%S')}")

        event_duration_delta = end_time - start_time

        event_duration_minutes = int(event_duration_delta.total_seconds() / 60)
        event_duration_hour = 0

        if event_duration_minutes > 59:
            event_duration_hour = int(event_duration_minutes // 60)
            event_duration_minutes = event_duration_minutes % 60

        if event_duration_minutes > 59:
            logger.warning(f"event_duration_minutes > 59, {event_duration_minutes=}")
            event_duration_minutes = 59
        if event_duration_hour > 24:
            logger.warning(f"event_duration_hour > 24, {event_duration_hour=}")
            event_duration_hour = 24

        args = {
            "calendar_id": self._calendar_id,
            "summary": topic,
            # "description": None,
            # "location": "Google Meet",
            "start_datetime": start_time.isoformat(),
            "event_duration_minutes": event_duration_minutes,
            "event_duration_hour": event_duration_hour,
            "timezone": "Europe/Moscow",
            "send_updates": False,
        }

        self._logger.debug(f"create calendar event with args {args}")

        res = self._composio.tools.execute(
            slug="GOOGLECALENDAR_CREATE_EVENT",
            arguments=args,
            user_id=self._user_id,
        )

        if not res["successful"]:
            raise ValueError(res["error"])

        self._logger.debug(f"event created: {res}")
