from sqlalchemy import Engine, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from voice_assistant.app_utils.app_types import UserId
from voice_assistant.database.schema import CalendarModel


class CalendarDataService:
    def __init__(self, engine: Engine, user_id: UserId):
        self._engine = engine
        self.user_id = user_id

    def load_calendar_data(self) -> CalendarModel | None:
        with Session(self._engine) as session:
            try:
                stmt = select(CalendarModel).where(CalendarModel.user_id == self.user_id)
                return session.scalar(stmt)

            except NoResultFound:
                return None

    def save_calendar_data(self, calendar_data: CalendarModel) -> None:
        with Session(self._engine) as session:
            stmt = select(CalendarModel).where(CalendarModel.user_id == calendar_data.user_id)
            result = session.scalar(stmt)

            if result:
                result.token_data = calendar_data.token_data
                result.calendar_id = calendar_data.calendar_id
            else:
                session.add(calendar_data)

            session.commit()
