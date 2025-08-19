from voice_assistant.app_interfaces.toolset import Toolset
from voice_assistant.app_utils.app_types import UserId
from voice_assistant.database.calendar_data.calendar_data import CalendarDataService
from voice_assistant.database.core import engine
from voice_assistant.services.calendar.service import CalendarService
from voice_assistant.services.composio.factory import create_composio


async def get_activity_logger(user_id: UserId) -> Toolset:
    from voice_assistant.tools.activity_logger.tools import ActivityLoggerToolset  # noqa: PLC0415

    calendar_data_service = CalendarDataService(engine, user_id)
    user_data = calendar_data_service.load_calendar_data()
    if user_data is None:
        raise RuntimeError(f"has no calendar data for {user_id.log()}")

    composio = await create_composio(user_id)

    calendar_service = CalendarService(user_id, user_data.calendar_id, composio)

    return ActivityLoggerToolset(user_id, calendar_service)
