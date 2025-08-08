#!/usr/bin/env python3
"""
Скрипт для добавления записи о тренировке в Google Sheets по требованиям:
- Аутентификация через google.oauth2.credentials.Credentials
- Определение диапазона столбцов для конкретного упражнения
- Поиск последней непустой строки в рамках диапазона упражнения
- Формирование и добавление новой строки
"""

import argparse
import asyncio
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from loguru import logger

from voice_assistant.app_utils.app_types import UserId
from voice_assistant.database.core import engine
from voice_assistant.services.calendar.calendar_data import CalendarDataService
from voice_assistant.services.calendar.creds import get_calendar_credentials
from voice_assistant.services.google_settings import calendar_settings


def col_idx_to_letter(idx: int) -> str:
    """Преобразовать индекс столбца (1-based) в букву, например 1->A, 27->AA"""
    result = ""
    while idx > 0:
        idx, rem = divmod(idx - 1, 26)
        result = chr(65 + rem) + result
    return result


def calc_total(reps: list[int], bonus: int) -> int:
    """Сумма повторений плюс бонус"""
    return sum(r for r in reps if r) + bonus


class WorkoutSheetAppender:
    def __init__(
        self,
        creds: Credentials,
        spreadsheet_id: str,
        sheet_name: str,
        exercise_name: str,
    ):
        self.service = build("sheets", "v4", credentials=creds)
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.exercise_name = exercise_name

    def _get_header_row(self) -> list[str]:
        range_ = f"{self.sheet_name}!1:1"
        result = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_).execute()
        return result.get("values", [[]])[0]

    def _find_exercise_range(self) -> tuple[int, int]:
        header = self._get_header_row()
        # найти индекс начала упражнения
        try:
            start_idx = header.index(self.exercise_name) + 1  # 1-based
        except ValueError as e:
            raise e from ValueError(f"Упражнение '{self.exercise_name}' не найдено в заголовке")
        # определить конец диапазона до следующего непустого заголовка
        end_idx = start_idx
        for i in range(start_idx, len(header)):
            if header[i] != "":
                break
            end_idx += 1
        return start_idx, end_idx

    def _find_next_row(self, start_col: int, end_col: int) -> int:
        start_letter = col_idx_to_letter(start_col)
        end_letter = col_idx_to_letter(end_col)
        range_ = f"{self.sheet_name}!{start_letter}2:{end_letter}"
        result = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_).execute()
        rows = result.get("values", [])
        # ищем последнюю строку с данными в любом столбце диапазона
        # for idx in range(len(rows) - 1, -1, -1):
        #     if any(cell != "" for cell in rows[idx]):
        #         return idx + 2 + 1
        return len(rows) + 2 + 1  # +2 чтобы перейти от 0-based к реальному номеру ряда плюс одна пустая строка

    def append_workout(self, date: str, reps: list[int], bonus: int, total: int | None = None) -> None:
        if total is None:
            total = calc_total(reps, bonus)
        start_col, end_col = self._find_exercise_range()
        row_idx = self._find_next_row(start_col, end_col)
        # подготавливаем полную строку: дата + 6 сетов + 🔥 + добавка + сумма
        fire = "🔥"
        cells = [date] + [str(r) if r is not None else "" for r in reps] + [fire, str(bonus), str(total)]
        range_ = f"{self.sheet_name}!A{row_idx}"
        body = {"values": [cells]}
        logger.info(f"Добавляем строку в {range_}: {cells}")
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()
        logger.success(f"Запись добавлена в строку {row_idx}")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Добавление записи о тренировке в Google Sheets")
    parser.add_argument("--spreadsheet-id", required=True)
    parser.add_argument("--sheet-name", required=True)
    parser.add_argument("--exercise-name", required=True)
    parser.add_argument("--reps", nargs="*", type=int, help="Повторы для сетов (от 1 до 6)", default=[])
    parser.add_argument("--bonus", type=int, help="Значение добавки", default=0)
    parser.add_argument(
        "--date",
        help="Дата в формате DD.MM.YYYY",
        default=datetime.now(tz=calendar_settings.calendar_tz).strftime("%d.%m.%Y"),
    )
    parser.add_argument("--total", type=int, help="Всего (сумма), если не передана, вычисляется автоматически")
    args = parser.parse_args()

    calendar_data_service = CalendarDataService(engine, UserId("default"))
    creds = await get_calendar_credentials(calendar_data_service, refresh=False)

    # # аутентификация
    # creds_file = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
    # creds = Credentials.from_authorized_user_file(creds_file)

    appender = WorkoutSheetAppender(creds, args.spreadsheet_id, args.sheet_name, args.exercise_name)
    appender.append_workout(args.date, args.reps + [None] * (6 - len(args.reps)), args.bonus, args.total)


if __name__ == "__main__":
    asyncio.run(main())
