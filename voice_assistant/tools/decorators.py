import functools
import sys
import traceback
from typing import Any, Awaitable, Callable, ParamSpec

P = ParamSpec("P")


def log_tool_decorator[**P](func: Callable[P, Awaitable[str]], logger: Any) -> Callable[P, Awaitable[str]]:
    logger = logger.bind(action="tool")

    @functools.wraps(func)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> str:
        logger.info(f"CALL '{func.__name__}' with args {args}, kwargs {kwargs} ")
        try:
            res = await func(*args, **kwargs)
        except Exception as exc:
            logger.exception(f"FAIL call tool: {exc}")
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
            raise exc

        res = f"Сообщи пользователю что ты — {res}"

        logger.info(f"DONE '{func.__name__}' with result: '{res}'")

        return res

    return wrapped
