import os
import time
import logging
from collections import deque
from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

load_dotenv()  # Load environment variables from .env file

logger = logging.getLogger("RateLimit")

WINDOW_SECONDS = 60

# Max requests per client ip per minute, every endpoint together
DEFAULT_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))

# Stricter limits per path, against password guessing and spam sign ups
PATH_LIMITS = {
    "/auth/login": int(os.getenv("RATE_LIMIT_LOGIN_PER_MINUTE", "5")),
    "/auth/register": int(os.getenv("RATE_LIMIT_REGISTER_PER_MINUTE", "5")),
}


# Limits requests per client ip in a sliding window of one minute
# Counts are kept in memory, so each worker process has its own counts
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.hits: dict[tuple[str, str], deque] = {}
        self.last_cleanup = time.monotonic()

    async def dispatch(self, request: Request, call_next):
        # CORS preflight requests are not counted
        if request.method == "OPTIONS":
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        self.cleanup(now)

        path = request.url.path.rstrip("/") or "/"
        checks = [(("all", ip), DEFAULT_LIMIT)]
        if path in PATH_LIMITS:
            checks.append(((path, ip), PATH_LIMITS[path]))

        # Reject if any limit is reached, then count the request against all of them
        for key, limit in checks:
            hits = self.hits.setdefault(key, deque())
            while hits and hits[0] <= now - WINDOW_SECONDS:
                hits.popleft()
            if len(hits) >= limit:
                retry_after = int(hits[0] + WINDOW_SECONDS - now) + 1
                logger.warning(f"Rate limit reached: {ip} {request.method} {path}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": f"Too many requests, try again in {retry_after} seconds"},
                    headers={"Retry-After": str(retry_after)},
                )

        for key, _ in checks:
            self.hits[key].append(now)

        return await call_next(request)

    # Drop ips with no requests in the last window, so memory does not grow
    def cleanup(self, now: float):
        if now - self.last_cleanup < WINDOW_SECONDS:
            return
        self.last_cleanup = now
        for key in [k for k, hits in self.hits.items() if not hits or hits[-1] <= now - WINDOW_SECONDS]:
            del self.hits[key]
