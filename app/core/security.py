from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings
from app.core.redis_client import redis_client
import time

# API Key Dependency
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    # Simple check for now. In prod, check DB or Redis for valid keys.
    # We will assume a static list or single key for prototype.
    if api_key_header == settings.API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )

class RateLimiter:
    def __init__(self, times: int = 10, seconds: int = 60):
        self.times = times
        self.seconds = seconds

    async def __call__(self, api_key: str = Depends(get_api_key)):
        # Rate limit key per API key
        key = f"rate_limit:{api_key}"
        
        # Redis logic (Token Bucket / Sliding Window simplified)
        current = redis_client.incr(key)
        if current == 1:
            redis_client.expire(key, self.seconds)
            
        if current > self.times:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

# Dependencies to be used in routes
verify_api_key = Depends(get_api_key)
rate_limit_standard = Depends(RateLimiter(times=100, seconds=60)) # 100 req/min
