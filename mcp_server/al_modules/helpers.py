from datetime import datetime

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from loguru import logger

from mcp_server.al_modules.database import Contex

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Авторизация
flow = InstalledAppFlow.from_client_secrets_file("../.cache/credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

# Создание сервиса
calendar_service = build("calendar", "v3", credentials=creds)


async def commit_new_activity(
    activity_topic: str,
    command_context: Contex,
) -> str:
    current_time = datetime.now()  # noqa: DTZ005

    response_message = ""

    last_activity_topic = command_context.last_activity_topic
    last_activity_time = command_context.last_activity_time
    if last_activity_topic and last_activity_time:
        await _jot_down_activity(
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
    command_context: Contex,
) -> str:
    current_time = datetime.now()  # noqa: DTZ005

    last_activity_topic = command_context.last_activity_topic
    last_activity_time = command_context.last_activity_time

    if last_activity_topic and last_activity_time:
        await _jot_down_activity(
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
        calendar_service.events()
        .insert(
            calendarId="1390da56718a398ff28cdefb909fffc3aa55bc7aea60faafdbed20e5c9e2121a@group.calendar.google.com",
            body=event,
        )
        .execute()
    )
    logger.info("event created: {}".format(event.get("htmlLink")))
