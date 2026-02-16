import redis
from app.core.config import settings

# Output a simple synchronous client for API usage
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=1, # Use DB 1 for batch metadata (0 is often default involved with Celery)
    decode_responses=True
)
