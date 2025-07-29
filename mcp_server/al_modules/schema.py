from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ContexModel(Base):
    __tablename__ = "contex"

    id: Mapped[int] = mapped_column(primary_key=True)
    last_activity_topic: Mapped[str | None] = mapped_column(String, nullable=True)
    last_activity_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
