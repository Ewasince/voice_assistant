import os
from datetime import datetime


def get_current_time(*args):
    cur_time = datetime.now()
    print(f"Сейчас время: {cur_time}")
    return


def get_os_type(*args):
    os_type = os.name
    print(f"Твоя система – {os_type}")
