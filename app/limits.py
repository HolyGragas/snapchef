"""Simple in-memory usage limits, so a public demo can't run up a big API bill."""

import time
from collections import defaultdict, deque


class UsageLimiter:
    def __init__(self, per_ip_per_hour: int, total_per_day: int):
        self.per_ip_per_hour = per_ip_per_hour
        self.total_per_day = total_per_day
        self._by_ip: dict[str, deque[float]] = defaultdict(deque)
        self._all: deque[float] = deque()

    @staticmethod
    def _trim(times: deque[float], window: float, now: float) -> None:
        while times and now - times[0] > window:
            times.popleft()

    def check(self, ip: str) -> str | None:
        """Record a request. Returns an error message if a limit is reached, else None."""
        now = time.monotonic()
        self._trim(self._all, 86400, now)
        if self.total_per_day > 0 and len(self._all) >= self.total_per_day:
            return "SnapChef has reached its daily limit. Please try again tomorrow."

        mine = self._by_ip[ip]
        self._trim(mine, 3600, now)
        if self.per_ip_per_hour > 0 and len(mine) >= self.per_ip_per_hour:
            return "You've made a lot of requests. Please wait a bit and try again."

        mine.append(now)
        self._all.append(now)
        return None
