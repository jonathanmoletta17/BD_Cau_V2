import time
from typing import Any, Dict, Tuple


class Cache:
    def __init__(self, ttl_seconds: int = 60):
        self.ttl = ttl_seconds
        self.store: Dict[str, Tuple[float, Any]] = {}

    def _now(self) -> float:
        return time.time()

    def get(self, key: str):
        x = self.store.get(key)
        if not x:
            return None
        ts, val = x
        if self._now() - ts > self.ttl:
            self.store.pop(key, None)
            return None
        return val

    def set(self, key: str, value: Any):
        self.store[key] = (self._now(), value)

