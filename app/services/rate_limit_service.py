from collections import deque
from time import monotonic

from fastapi import HTTPException


class RateLimiter:
    def __init__(
        self,
        limit: int,
        window_seconds: int,
        detail: str,
    ):
        self.limit = limit
        self.window_seconds = window_seconds
        self.detail = detail
        self.attempts: dict[str, deque[float]] = {}

    def check(self, key: str) -> None:
        now = monotonic()

        attempts = self.attempts.setdefault(
            key,
            deque(),
        )

        while (
            attempts
            and now - attempts[0] >= self.window_seconds
        ):
            attempts.popleft()

        if len(attempts) >= self.limit:
            raise HTTPException(
                status_code=429,
                detail=self.detail,
            )

    def add_attempt(self, key: str) -> None:
        self.attempts.setdefault(
            key,
            deque(),
        ).append(monotonic())

    def reset(self, key: str) -> None:
        self.attempts.pop(key, None)

    def clear(self) -> None:
        self.attempts.clear()


login_rate_limiter = RateLimiter(
    limit=5,
    window_seconds=60,
    detail="Too many login attempts",
)

register_rate_limiter = RateLimiter(
    limit=5,
    window_seconds=60,
    detail="Too many registration attempts",
)