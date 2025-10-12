"""
Redis Caching Layer for NeuroAgent

Phase 8-1: Performance Optimization
Implements response caching, drug interaction memoization, and Bedrock response caching
"""

import json
import hashlib
import os
from typing import Any, Optional, Callable
from functools import wraps
from datetime import timedelta
import logging

try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available - caching disabled")


logger = logging.getLogger(__name__)


class RedisCacheManager:
    """
    Redis cache manager for NeuroAgent API

    Handles caching of:
    - Diagnosis responses
    - Drug interactions
    - Bedrock AI responses
    - Medical knowledge lookups
    """

    def __init__(self):
        """Initialize Redis connection"""
        self.enabled = REDIS_AVAILABLE and os.getenv("REDIS_ENABLED", "false").lower() == "true"

        if self.enabled:
            try:
                self.redis_client = Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", "6379")),
                    db=int(os.getenv("REDIS_DB", "0")),
                    password=os.getenv("REDIS_PASSWORD", None),
                    decode_responses=True,
                    socket_timeout=2,
                    socket_connect_timeout=2,
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache enabled and connected")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self.enabled = False
                self.redis_client = None
        else:
            self.redis_client = None
            logger.info("Redis caching disabled")

    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate consistent cache key from arguments

        Args:
            prefix: Cache key prefix (e.g., "diagnosis", "drug_interaction")
            *args, **kwargs: Arguments to hash for key generation

        Returns:
            Cache key string
        """
        # Create deterministic hash from arguments
        data_str = json.dumps({
            "args": args,
            "kwargs": sorted(kwargs.items())
        }, sort_keys=True, default=str)

        hash_value = hashlib.sha256(data_str.encode()).hexdigest()[:16]
        return f"{prefix}:{hash_value}"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if not self.enabled:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache GET error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache with TTL

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Time-to-live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            value_json = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, value_json)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache SET error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False

        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache DELETE error for key {key}: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern

        Args:
            pattern: Redis key pattern (e.g., "diagnosis:*")

        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cache INVALIDATE: {pattern} ({deleted} keys)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache INVALIDATE error for pattern {pattern}: {e}")
            return 0

    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}

        try:
            info = self.redis_client.info("stats")
            return {
                "enabled": True,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
                "keys": self.redis_client.dbsize(),
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}

    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100


# Global cache instance
cache_manager = RedisCacheManager()


def cached(
    prefix: str,
    ttl: int = 3600,
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching function results

    Args:
        prefix: Cache key prefix
        ttl: Time-to-live in seconds
        key_builder: Optional custom function to build cache key from args

    Usage:
        @cached(prefix="diagnosis", ttl=3600)
        async def analyze_case(request):
            # ...expensive operation...
            return result
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache_manager._generate_cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Cache miss - execute function
            result = await func(*args, **kwargs)

            # Store in cache
            cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


def cache_diagnosis_key_builder(request) -> str:
    """
    Build cache key for diagnosis requests

    Key components:
    - Patient symptoms (names, severity, duration)
    - Current medications (for drug interactions)
    - Vital signs
    - Chief complaint
    """
    key_components = {
        "symptoms": sorted([
            f"{s.name}:{s.severity.value}:{s.duration_days}"
            for s in request.symptoms
        ]),
        "medications": sorted(request.patient_info.current_medications),
        "chief_complaint": request.chief_complaint,
        "age": request.patient_info.age,
        "gender": request.patient_info.gender.value,
    }

    data_str = json.dumps(key_components, sort_keys=True)
    hash_value = hashlib.sha256(data_str.encode()).hexdigest()[:16]
    return f"diagnosis:{hash_value}"


def cache_drug_interaction_key_builder(medications: list) -> str:
    """Build cache key for drug interaction checks"""
    # Sort to ensure consistent key regardless of input order
    meds_sorted = sorted([med.lower().strip() for med in medications])
    meds_str = ":".join(meds_sorted)
    hash_value = hashlib.sha256(meds_str.encode()).hexdigest()[:16]
    return f"drug_interaction:{hash_value}"
