from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any, Optional


class _LRUCache:
    """In-process LRU cache with TTL. Safe for serverless (no disk writes)."""

    def __init__(self, maxsize: int = 128, ttl: int = 21600) -> None:
        self._store: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._maxsize = maxsize
        self._ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, exp = entry
        if time.monotonic() > exp:
            del self._store[key]
            return None
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        exp = time.monotonic() + (ttl if ttl is not None else self._ttl)
        self._store[key] = (value, exp)
        self._store.move_to_end(key)
        while len(self._store) > self._maxsize:
            self._store.popitem(last=False)


cache = _LRUCache()
