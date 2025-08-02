from agents import Tool, function_tool

from voice_assistant.app_interfaces.toolset import Toolset
from voice_assistant.app_utils.types import UserId
from voice_assistant.database.core import engine
from voice_assistant.services.calendar.calendar_data import CalendarDataService
from voice_assistant.services.calendar.creds import get_calendar_credentials
from voice_assistant.services.calendar.service import CalendarService
from voice_assistant.services.memory import ContextMemoryService


class ActivityLoggerToolset(Toolset):
    def __init__(self, user_id: UserId, calendar_service: CalendarService) -> None:
        super().__init__()
        self._user_id = user_id
        self._calendar_service: CalendarService = calendar_service

        self._memory_service = ContextMemoryService(user_id)

        self._logger = self._logger.bind(user_id=user_id, action="tool")

    async def get_tools(self) -> list[Tool]:
        return [
            self.log_new_activity,
            self.log_end_activity,
        ]

    @function_tool()
    async def log_new_activity(
        self,
        new_activity: str,
        new_activity_offset: str | None = None,
    ) -> str:
        """Log a new activity event.
        Trigger this tool when the user indicates they are currently engaged in an activity or have just started one.

        Args:
            new_activity: Name of the started activity. Should be short, precise, and sound natural to a human —
                like a familiar, conventional label for the activity. Avoid synonyms, verb forms, or uncommon phrasings.
            new_activity_offset: Time since activity started (optional). Provide this only if the user explicitly
                mentioned how long ago the activity began. The value must be in the %H:%M:%S format —
                for example: "00:10:45" (10 minutes and 45 seconds ago).
        """

        self._logger.info(f"log_new_activity: {new_activity=} {new_activity_offset=}")

        if self._calendar_service is None:
            raise RuntimeError("Calendar service was not initialized")

        context = self._memory_service.load_contex()
        response = await self._calendar_service.commit_new_activity(new_activity, context)
        self._memory_service.save_contex(context)

        # response = f"я записал, что начал активность '{new_activity}'"
        #
        # if new_activity_offset:
        #     dt_offset = datetime.strptime(new_activity_offset, "%H:%M:%S")
        #     delta = timedelta(hours=dt_offset.hour, minutes=dt_offset.minute, seconds=dt_offset.second)
        #     delta_minutes = delta.seconds / 60
        #     response += f" {delta_minutes:.2f} минут назад"

        return response

    @function_tool()
    async def log_end_activity(
        self,
        end_activity_offset: str | None = None,
    ) -> str:
        """Log an activity event that ended.
        Use this tool only if the user has stated that an activity is finished AND has NOT mentioned being currently
        engaged in another activity or just starting one.

        Args:
            end_activity_offset: Time since activity ended (optional). Provide this only if the user explicitly
                mentioned how long ago the activity ended. The value must be in the %H:%M:%S format —
                for example: "00:10:45" (10 minutes and 45 seconds ago).
        """

        self._logger.info(f"log_end_activity: {end_activity_offset=}")

        if self._calendar_service is None:
            raise RuntimeError("Calendar service was not initialized")

        context = self._memory_service.load_contex()
        response = await self._calendar_service.commit_end_activity(context)
        self._memory_service.save_contex(context)

        # response = "я записал, что закончил активность"
        #
        # dt_offset = datetime.strptime(end_activity_offset or "00:00:00", "%H:%M:%S")
        # delta = timedelta(hours=dt_offset.hour, minutes=dt_offset.minute, seconds=dt_offset.second)
        # delta_minutes = delta.seconds / 60
        #
        # if delta_minutes:
        #     response += f" {delta_minutes:.2f} минут назад"

        return response


async def get_activity_logger(user_id: UserId) -> ActivityLoggerToolset:
    calendar_data_service = CalendarDataService(engine, user_id)
    creds = await get_calendar_credentials(calendar_data_service)

    user_data = calendar_data_service.load_calendar_data()

    if user_data is None:
        raise RuntimeError(f"has no calendar data for {user_id.log()}")

    calendar_service = CalendarService(user_id, creds, user_data.calendar_id)

    return ActivityLoggerToolset(user_id, calendar_service)
