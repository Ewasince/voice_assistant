from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from loguru import logger

from voice_assistant.database.models import Contex
from voice_assistant.tools.activity_logger.al_modules.settings import al_settings


class CalendarService:
    def __init__(self) -> None:
        creds = self._get_credentials()
        self._calendar_service = build("calendar", "v3", credentials=creds)

    async def commit_new_activity(
        self,
        activity_topic: str,
        command_context: Contex,
    ) -> str:
        current_time = datetime.now(tz=al_settings.calendar_tz)

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
        current_time = datetime.now(tz=al_settings.calendar_tz)

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
                calendarId=al_settings.calendar_id,
                body=event,
            )
            .execute()
        )
        logger.info("event created: {}".format(event.get("htmlLink")))

    def _get_credentials(self) -> Credentials:
        creds = None

        # 1) Пробуем загрузить сохранённые креды
        if al_settings.calendar_token_file.exists():
            creds = Credentials.from_authorized_user_file(
                str(al_settings.calendar_token_file),
                al_settings.calendar_scopes,
            )

        # 2) Если нет или невалидны — обновляем/получаем заново
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("refreshing Google OAuth token...")
                creds.refresh(Request())
            else:
                logger.info("running OAuth flow in browser...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(al_settings.calendar_creds_file),
                    al_settings.calendar_scopes,
                )
                # Важно: offline, чтобы получить refresh_token один раз
                creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

            # 3) Сохраняем для будущих запусков
            al_settings.calendar_token_file.parent.mkdir(parents=True, exist_ok=True)
            with al_settings.calendar_token_file.open("w") as f:
                f.write(creds.to_json())

        return creds
