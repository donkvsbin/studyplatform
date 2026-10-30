from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from flask import current_app
from ..api.common import ApiError


class RateLimiter:
    """Single-process local demo limiter. State resets when the process restarts."""

    def __init__(self):
        self.entries = defaultdict(deque)
        self.lock = Lock()

    def check(self, key, limit, seconds):
        if not current_app.config["RATE_LIMIT_ENABLED"]:
            return
        now = monotonic()
        with self.lock:
            # Evict expired buckets, including abandoned IP addresses.
            for old in list(self.entries):
                if not self.entries[old] or now - self.entries[old][-1] > 900:
                    del self.entries[old]
            bucket = self.entries[key]
            while bucket and now - bucket[0] >= seconds:
                bucket.popleft()
            if len(bucket) >= limit:
                raise ApiError("rate_limited", 429)
            bucket.append(now)


def throttle(key, limit, seconds=900):
    current_app.extensions["learnhub_limiter"].check(key, limit, seconds)
