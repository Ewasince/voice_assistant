from datetime import datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ContexModel(Base):
    __tablename__ = "contex"

    session_name: Mapped[str] = mapped_column(String, primary_key=True)
    last_activity_topic: Mapped[str | None] = mapped_column(String, nullable=True)
    last_activity_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class CalendarModel(Base):
    __tablename__ = "calendar_data"

    user_id: Mapped[str] = mapped_column(primary_key=True)
    token_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    creds_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    calendar_id: Mapped[str] = mapped_column(String, nullable=False)
