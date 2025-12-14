from typing import Any, Self

from django.core.cache import cache


class ConfigCache:
    CACHE_KEY_PREFIX = "config:"
    # Sentinel value to distinguish between "key doesn't exist" and "value is None"
    _NOT_FOUND = object()

    _instance: Self | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get(self, key: str) -> Any | None:
        """Get value from cache. Returns _NOT_FOUND if key doesn't exist."""
        full_key = self.CACHE_KEY_PREFIX + key
        # Use a sentinel to distinguish between "key doesn't exist" and "value is None"
        value = cache.get(full_key, self._NOT_FOUND)
        if value is self._NOT_FOUND:
            return self._NOT_FOUND
        return value

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        return self.get(key) is not self._NOT_FOUND

    def set(self, key: str, value: Any) -> None:
        cache.set(self.CACHE_KEY_PREFIX + key, value)

    def invalidate(self, key: str) -> None:
        cache.delete(self.CACHE_KEY_PREFIX + key)


# Singleton instance
config_cache = ConfigCache()
