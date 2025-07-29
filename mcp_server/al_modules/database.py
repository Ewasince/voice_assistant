from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from mcp_server.al_modules.schema import Base, ContexModel
from mcp_server.al_modules.settings import ALSettings


@dataclass
class Contex:
    last_activity_topic: str | None = None
    last_activity_time: datetime | None = None


class MemoryService:
    def __init__(self, settings: ALSettings = None):
        settings = settings or ALSettings()
        self._engine = create_engine(settings.database_uri, echo=False)

        self.ensure_db()

    def ensure_db(self):
        Base.metadata.create_all(self._engine)

    def save_contex(self, contex: Contex, record_id: int = 1):
        with Session(self._engine) as session:
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
        with Session(self._engine) as session:
            try:
                db_obj = session.query(ContexModel).filter_by(id=record_id).one()
                return Contex(
                    last_activity_topic=db_obj.last_activity_topic, last_activity_time=db_obj.last_activity_time
                )
            except NoResultFound:
                return Contex()
