from datetime import datetime, timedelta

from voice_assistant.services.google_settings import calendar_settings


def parse_datetime(value: str) -> datetime:
    dt = datetime.strptime(value, "%H:%M")  # noqa: DTZ007
    dt = datetime.combine(datetime.now(tz=calendar_settings.calendar_tz), dt.time())
    return calendar_settings.calendar_tz.localize(dt)


def parse_timedelta(value: str) -> timedelta:
    """
    Преобразует строку в timedelta.
    Поддерживает:
      - ISO 8601 duration: PT15M, PT1H30M, -PT45M
      - HH:MM:SS и -HH:MM:SS
    """
    value = value.strip()

    if not value:
        raise ValueError(f"parse_timedelta value {value!r} is empty")

    # # ISO 8601 duration
    # if value.upper().startswith("P") or value.upper().startswith("-P"):
    #     negative = value.startswith("-")
    #     if negative:
    #         value = value[1:]  # убираем минус перед "P"
    #     # простой парс через dateutil
    #     duration = isoduration.parse_duration(value)
    #     return -duration if negative else duration

    # HH:MM:SS
    # match = re.match(r"^(-)?(?:(\d+):)?(\d{1,2}):(\d{1,2})$", value)
    # if match:
    #     negative, hours, minutes, seconds = match.groups()
    #     hours = int(hours or 0)
    #     minutes = int(minutes)
    #     seconds = int(seconds)
    #     delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    #     return -delta if negative else delta

    negative = False
    if value[0] in [
        "−",
        "-",
        "‐",
        "—",
    ]:
        negative = True
        value = value[1:]

    dt_offset = datetime.strptime(value, "%H:%M:%S")  # noqa: DTZ007
    delta = timedelta(hours=dt_offset.hour, minutes=dt_offset.minute, seconds=dt_offset.second)

    return delta * -1 if negative else delta
