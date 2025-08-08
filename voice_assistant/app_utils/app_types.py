from typing import Any, Awaitable, Callable, Final, Generator, Self


class UserId(str):
    def log(self) -> str:
        return f"user '{self}'"

    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any, *args: Any) -> Self:
        if not isinstance(value, str):
            raise TypeError("UserId must be a string")
        return cls(value)


DEFAULT_USER_ID: Final[UserId] = UserId("default")

type CommandPerformerFunction = Callable[[str], Awaitable[str | None]]
