import functools
from typing import Awaitable, Callable, ParamSpec, TypeVar

from loguru import Logger

P = ParamSpec("P")
R = TypeVar("R")


def tool_decorator[**P, R](func: Callable[P, Awaitable[R]], logger: Logger) -> Callable[P, Awaitable[R]]:
    @functools.wraps(func)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.bind(action="tool").info(f" do  '{func.__name__}' with args {args}, kwargs {kwargs} ")
        res = await func(*args, **kwargs)
        logger.bind(action="tool").info(f"done '{func.__name__}' with res {res}")
        return res

    return wrapped
