import logging
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях (в памяти процесса).
sessionStorage: dict[str, dict[str, Any]] = {}


class Req(BaseModel):
    version: str
    session: str


@app.post("/")
async def main(request: Req) -> JSONResponse:
    """
    Принимает POST с JSON телом и возвращает ответ в формате,
    совместимом с исходной логикой.
    """
    req_json: dict[str, Any] = request.model_dump_json()  # type: ignore[assignment]
    logging.info(f"Request: {req_json}")
    logging.info("Request: %r", req_json)

    response: dict[str, Any] = {
        "version": req_json["version"],
        "session": req_json["session"],
        "response": {"end_session": False},
    }

    handle_dialog(req_json, response)

    logging.info("Response: %r", response)
    # ensure_ascii=False, indent=2 — как в исходнике
    return JSONResponse(content=response, media_type="application/json; charset=utf-8")


def handle_dialog(req: dict[str, Any], res: dict[str, Any]) -> None:
    user_id = req["session"]["user_id"]

    if req["session"].get("new"):
        # Новый пользователь: инициализируем сессию и приветствуем.
        sessionStorage[user_id] = {
            "suggests": [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res["response"]["text"] = "Привет! Купи слона!"
        res["response"]["buttons"] = get_suggests(user_id)
        return

    # Обрабатываем ответ пользователя.
    utterance = (req.get("request", {}).get("original_utterance") or "").lower()
    if utterance in {"ладно", "куплю", "покупаю", "хорошо"}:
        res["response"]["text"] = "Слона можно найти на Яндекс.Маркете!"
        return

    # Если нет — убеждаем купить слона!
    res["response"]["text"] = 'Все говорят "{}", а ты купи слона!'.format(
        req.get("request", {}).get("original_utterance", "")
    )
    res["response"]["buttons"] = get_suggests(user_id)


def get_suggests(user_id: str) -> list:
    session = sessionStorage.get(user_id, {"suggests": []})
    suggests = [{"title": s, "hide": True} for s in session["suggests"][:2]]

    # Сдвигаем список, чтобы подсказки менялись.
    session["suggests"] = session["suggests"][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка — добавляем кнопку со ссылкой.
    if len(suggests) < 2:
        suggests.append({"title": "Ладно", "url": "https://market.yandex.ru/search?text=слон", "hide": True})
    return suggests


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
