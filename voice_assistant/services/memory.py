from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from voice_assistant.app_utils.app_types import UserId
from voice_assistant.app_utils.settings import get_settings
from voice_assistant.database.core import engine
from voice_assistant.database.models import Contex
from voice_assistant.database.schema import ContexModel


class ContextMemoryService:
    def __init__(self, user_id: UserId):
        self._session_name = _get_session_name_from_user_id(user_id)
        self._tz = get_settings(user_id).calendar_settings.tz

    def save_contex(self, contex: Contex) -> None:
        with Session(engine) as session:
            try:
                existing = session.query(ContexModel).filter_by(session_name=self._session_name).one()
                existing.last_activity_topic = contex.last_activity_topic
                existing.last_activity_time = contex.last_activity_time
            except NoResultFound:
                new_record = ContexModel(
                    session_name=self._session_name,
                    last_activity_topic=contex.last_activity_topic,
                    last_activity_time=contex.last_activity_time,
                )
                session.add(new_record)
            session.commit()

    def load_contex(self) -> Contex:
        with Session(engine) as session:
            try:
                db_obj = session.query(ContexModel).filter_by(session_name=self._session_name).one()
                last_activity_time = db_obj.last_activity_time
                if last_activity_time is not None:
                    last_activity_time = self._tz.localize(last_activity_time)
                return Contex(last_activity_topic=db_obj.last_activity_topic, last_activity_time=last_activity_time)
            except NoResultFound:
                return Contex()


def _get_session_name_from_user_id(user_id: UserId) -> str:
    return f"session-{user_id}"
