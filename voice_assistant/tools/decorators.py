import functools
import inspect
import sys
import traceback
from typing import Any, Awaitable, Callable, ParamSpec

P = ParamSpec("P")


def log_tool_decorator[**P](func: Callable[P, Awaitable[str]], logger: Any) -> Callable[P, Awaitable[str]]:
    logger = logger.bind(action="tool")
    signature = inspect.signature(func)

    @functools.wraps(func)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> str:
        try:
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            args_str = ", ".join(f"{k}={v!r}" for k, v in bound_args.arguments.items())
        except Exception as bind_exc:
            logger.exception(f"Could not bind arguments: {bind_exc}")
            args_str = f"args {args}, kwargs {kwargs}"

        logger.info(f"CALL '{func.__name__}' with: {args_str}")
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
