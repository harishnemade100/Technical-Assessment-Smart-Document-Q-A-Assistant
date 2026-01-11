import redis
import json
import os
from typing import Any, Optional


class RedisCache:
    """
    Lightweight Redis cache wrapper for embeddings, queries, etc.
    """

    def __init__(self):
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True  # store as strings
        )

    def get(self, key: str) -> Optional[Any]:
        """
        Fetch value from Redis and deserialize JSON.
        """
        value = self.client.get(key)
        if value is None:
            return None
        return json.loads(value)

    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Store value in Redis with TTL (default: 1 hour).
        """
        self.client.setex(
            key,
            ttl,
            json.dumps(value)
        )


# Singleton instance used across the app
redis_cache = RedisCache()
