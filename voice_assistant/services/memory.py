from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from voice_assistant.database.core import engine
from voice_assistant.database.models import Contex
from voice_assistant.database.schema import ContexModel


class MemoryService:
    def save_contex(self, contex: Contex, record_id: int = 1) -> None:
        with Session(engine) as session:
            try:
                existing = session.query(ContexModel).filter_by(id=record_id).one()
                existing.last_activity_topic = contex.last_activity_topic
                existing.last_activity_time = contex.last_activity_time
            except NoResultFound:
                new_record = ContexModel(
                    id=record_id,
                    last_activity_topic=contex.last_activity_topic,
                    last_activity_time=contex.last_activity_time,
                )
                session.add(new_record)
            session.commit()

    def load_contex(self, record_id: int = 1) -> Contex:
        with Session(engine) as session:
            try:
                db_obj = session.query(ContexModel).filter_by(id=record_id).one()
                return Contex(
                    last_activity_topic=db_obj.last_activity_topic, last_activity_time=db_obj.last_activity_time
                )
            except NoResultFound:
                return Contex()
