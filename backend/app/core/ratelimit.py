import time
from typing import Dict, Tuple
from fastapi import HTTPException, status
from app.core.config import settings

class RateLimiter:
    """
    In-memory per-user rate limiter for code execution & submissions.
    Stores last timestamp per (user_id, action_type).
    """
    def __init__(self):
        self._last_call: Dict[Tuple[str, str], float] = {}

    def check_rate_limit(self, user_id: str, action: str, min_interval_sec: float):
        now = time.time()
        key = (str(user_id), action)
        last_time = self._last_call.get(key, 0.0)
        elapsed = now - last_time
        
        if elapsed < min_interval_sec:
            retry_after = round(min_interval_sec - elapsed, 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please wait {retry_after} seconds before trying '{action}' again."
            )
        self._last_call[key] = now

rate_limiter = RateLimiter()
