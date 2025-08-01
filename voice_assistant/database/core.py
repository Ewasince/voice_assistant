from sqlalchemy import create_engine

from voice_assistant.app_utils.settings import primary_settings

engine = create_engine(primary_settings.database_uri, echo=False)

# Base.metadata.create_all(engine)
