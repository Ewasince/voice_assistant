from typing import Final, NewType

UserId = NewType("UserId", str)
DEFAULT_USER_ID: Final[UserId] = UserId("default")
