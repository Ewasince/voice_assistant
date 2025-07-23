from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import DateTime, String, create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


@dataclass
class Contex:
    last_activity_topic: str | None = None
    last_activity_time: datetime | None = None


engine = create_engine("sqlite:///data.db", echo=False)


class Base(DeclarativeBase):
    pass


class ContexModel(Base):
    __tablename__ = "contex"

    id: Mapped[int] = mapped_column(primary_key=True)
    last_activity_topic: Mapped[str | None] = mapped_column(String, nullable=True)
    last_activity_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


def init_db():
    Base.metadata.create_all(engine)


def save_contex(contex: Contex, record_id: int = 1):
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


def load_contex(record_id: int = 1) -> Contex:
    with Session(engine) as session:
        try:
            db_obj = session.query(ContexModel).filter_by(id=record_id).one()
            return Contex(last_activity_topic=db_obj.last_activity_topic, last_activity_time=db_obj.last_activity_time)
        except NoResultFound:
            return Contex()
