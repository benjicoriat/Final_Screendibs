"""Caching utilities for common database queries."""

import hashlib
import json
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional

# Simple in-memory cache with TTL
# For production, consider Redis or similar
_CACHE: Dict[str, tuple[Any, float]] = {}
DEFAULT_TTL = 300  # 5 minutes


def clear_cache() -> None:
    """Clear the entire cache."""
    global _CACHE
    _CACHE.clear()


def cache_key(*args: Any, **kwargs: Any) -> str:
    """Generate a cache key from function arguments."""
    key_data = {
        "args": str(args),
        "kwargs": json.dumps(kwargs, sort_keys=True, default=str),
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = DEFAULT_TTL) -> Callable:
    """
    Decorator to cache function results with TTL.

    Args:
        ttl: Time to live in seconds (default 300s)

    Usage:
        @cached(ttl=600)
        def get_user_summary(db, user_id):
            # expensive query
            return result
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = cache_key(*args, **kwargs)
            now = time.time()

            # Check if cached value exists and hasn't expired
            if key in _CACHE:
                cached_value, cached_time = _CACHE[key]
                if now - cached_time < ttl:
                    return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            _CACHE[key] = (result, now)
            return result

        return wrapper

    return decorator


class QueryCache:
    """Context manager for managing cache within a scope."""

    def __init__(self, enabled: bool = True) -> None:
        """
        Initialize cache context.

        Args:
            enabled: Whether caching is enabled (default True)
        """
        self.enabled = enabled
        self._cache_before: Dict[str, tuple[Any, float]] = {}

    def __enter__(self) -> "QueryCache":
        """Enter context manager."""
        if self.enabled:
            self._cache_before = _CACHE.copy()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager and restore cache state."""
        if self.enabled and exc_type is None:
            # Cache cleared on successful completion
            _CACHE.clear()
        elif not self.enabled:
            # Restore previous cache state
            _CACHE.clear()
            _CACHE.update(self._cache_before)

    def clear(self) -> None:
        """Manually clear cache within context."""
        _CACHE.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(_CACHE),
            "total_keys": len(_CACHE),
            "approximate_memory_usage": sum(
                len(str(k)) + len(str(v[0])) for k, v in _CACHE.items()
            ),
        }
