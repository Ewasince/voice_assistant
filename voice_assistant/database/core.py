from sqlalchemy import create_engine

from voice_assistant.database.schema import Base
from voice_assistant.settings import va_settings

engine = create_engine(va_settings.database_uri, echo=False)

Base.metadata.create_all(engine)
