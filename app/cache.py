import redis
import os
import json

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def set_cache(key: str, value: dict, expire: int = 3600):
    """Store a dictionary as JSON in Redis"""
    redis_client.set(key, json.dumps(value), ex=expire)

def get_cache(key: str):
    """Retrieve JSON dict from Redis"""
    data = redis_client.get(key)
    return json.loads(data) if data else None

def delete_cache(key: str):
    """Delete key from Redis"""
    redis_client.delete(key)
