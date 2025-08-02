from typing import Awaitable, Callable, Final, NewType

UserId = NewType("UserId", str)
DEFAULT_USER_ID: Final[UserId] = UserId("default")

type CommandPerformerFunction = Callable[[str], Awaitable[str | None]]
