from sqlalchemy import create_engine

from voice_assistant.app_utils.settings import get_settings

engine = create_engine(get_settings().database_uri, echo=False)

# Base.metadata.create_all(engine)
