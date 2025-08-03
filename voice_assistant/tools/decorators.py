import functools
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def log_tool_decorator[**P, R](func: Callable[P, Awaitable[R]], logger: Any) -> Callable[P, Awaitable[R]]:
    @functools.wraps(func)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.bind(action="tool").info(f"call '{func.__name__}' with args {args}, kwargs {kwargs} ")
        res = await func(*args, **kwargs)
        logger.bind(action="tool").info(f"done '{func.__name__}' with res {res}")
        return res

    return wrapped
