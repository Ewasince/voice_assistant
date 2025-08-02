import typer
from sqlalchemy import Engine, create_engine, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from typer import Typer

from voice_assistant.app_utils.types import UserId
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


app = Typer()


@app.command()
def cli_add(
    database_uri: str = typer.Option("sqlite:///data/data.db", help="URI к БД (например, sqlite:///data/data.db)"),
    user_id: str = typer.Option(..., help="ID пользователя"),
    calendar_id: str = typer.Option(..., help="ID календаря"),
) -> None:
    user_id_ = UserId(user_id)
    # Подключение к БД
    engine = create_engine(database_uri, echo=False)

    with Session(engine) as session:
        stmt = select(CalendarModel).where(CalendarModel.user_id == user_id_)
        result = session.scalar(stmt)

        if result:
            result.calendar_id = calendar_id
            typer.echo(f"Обновлены данные для {user_id_.log()}")
        else:
            new_entry = CalendarModel(user_id=user_id_, calendar_id=calendar_id)
            session.add(new_entry)
            typer.echo(f"Добавлена новая запись для {user_id_.log()}")

        session.commit()


if __name__ == "__main__":
    app()
